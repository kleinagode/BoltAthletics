import json
import os

from collections import defaultdict
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


class ScoutingReportGenerator:
    def __init__(self):
        self.report = defaultdict(dict)

    def generate_report(self, tracks, min_frames):
        player_stats = defaultdict(lambda: {"total_distance": 0, "speed_readings": [], "frames_present": 0})

        # Gather data from track file
        for frame_data in tracks['players']:
            for player_id, track in frame_data.items():
                player_stats[player_id]["frames_present"] += 1

                if "speed" in track:
                    player_stats[player_id]["speed_readings"].append(track["speed"])

                if "distance" in track:
                    player_stats[player_id]["total_distance"] += track["distance"]

        total_team_speed = 0
        total_team_distance = 0
        total_players = 0

        for player_id, stats in player_stats.items():
            frames = stats["frames_present"]
            
            # Skip false detections (e.g., players detected for only a few frames)
            if frames < min_frames:
                continue

            speed_vals = stats["speed_readings"]
            avg_speed = sum(speed_vals) / len(speed_vals) if speed_vals else 0
            total_distance = stats["total_distance"]

            distance_per_frame = total_distance / frames if frames > 0 else 0

            # Activity classification
            if distance_per_frame > 10:
                activity_level = "Highly Active"
            elif distance_per_frame > 5:
                activity_level = "Moderately Active"
            else:
                activity_level = "Low Activity"

            # Insightful notes
            notes = []
            if avg_speed > 8:
                notes.append("High-speed mover")
            if distance_per_frame < 2 and frames > 300:
                notes.append("Low movement for frame count – possible role player")

            # Add to report
            self.report[player_id] = {
                "average_speed": round(avg_speed, 2),
                "total_distance": round(total_distance, 2),
                "frames_present": frames,
                "activity_level": activity_level,
                "notes": notes
            }

            # Accumulate for team averages
            total_team_speed += avg_speed
            total_team_distance += total_distance
            total_players += 1

        # Add team-wide stats
        if total_players > 0:
            self.report["TEAM_AVERAGES"] = {
                "average_speed": round(total_team_speed / total_players, 2),
                "average_distance": round(total_team_distance / total_players, 2)
            }

        return self.report

    def save_as_json(self, path='output_reports/scouting_report.json'):
        # Convert keys to str to ensure JSON compatibility
        report_str_keys = {str(k): v for k, v in self.report.items()}
        
        with open(path, 'w') as f:
            json.dump(report_str_keys, f, indent=4)

    def save_as_pdf(self, path='output_reports/scouting_report.pdf', title="Scouting Report", logo_path=None):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        c = canvas.Canvas(path, pagesize=letter)
        width, height = letter

        # Add company logo (if available)
        if logo_path and os.path.exists(logo_path):
            logo_width, logo_height = 100, 50  # You can adjust this to fit your logo size
            c.drawImage(logo_path, 50, height - 50 - logo_height, logo_width, logo_height)


        # Title
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50 + 120, height - 50, title)  # Add 120 to offset for logo space

        y = height - 90
        c.setFont("Helvetica", 12)

        # Draw individual player stats with large separation between players
        for player_id, stats in self.report.items():
            if player_id == "TEAM_AVERAGES":
                continue  # Skip team averages here

            # Add a large separation between players
            y -= 30

            # Player info header
            c.setFont("Helvetica-Bold", 14)
            c.drawString(50, y, f"Player {player_id}:")
            y -= 20

            c.setFont("Helvetica", 12)

            # Each stat on a new line
            c.drawString(50, y, f"Average Speed: {stats['average_speed']} km/h")
            y -= 18
            c.drawString(50, y, f"Total Distance: {stats['total_distance']} m")
            y -= 18
            c.drawString(50, y, f"Frames: {stats['frames_present']}")
            y -= 18
            c.drawString(50, y, f"Activity Level: {stats['activity_level']}")
            y -= 18

            # Add notes (if any)
            if stats.get("notes"):
                notes_line = f"Notes: {', '.join(stats['notes'])}"
                c.drawString(50, y, notes_line)
                y -= 18

            if y < 60:  # Check for space on the page and move to the next page if necessary
                c.showPage()
                c.setFont("Helvetica", 12)
                y = height - 60

        # New page for team stats
        if "TEAM_AVERAGES" in self.report:
            c.showPage()
            c.setFont("Helvetica-Bold", 16)
            c.drawString(50, height - 50, "Team Averages")

            team_stats = self.report["TEAM_AVERAGES"]
            c.setFont("Helvetica", 12)
            y = height - 100
            c.drawString(50, y, f"Average Speed: {team_stats['average_speed']} km/h")
            y -= 20
            c.drawString(50, y, f"Average Distance: {team_stats['average_distance']} m")
            
        c.save()
