import json
import os
from collections import defaultdict
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF
from reportlab.lib import colors


class ScoutingReportGenerator:
    def __init__(self):
        self.report = defaultdict(dict)

    def generate_report(self, tracks, min_frames, game_stats_df=None):
        # Add scraped game stats at the top of the report
        if game_stats_df is not None:
            self.display_game_stats(game_stats_df)

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

    def display_game_stats(self, game_stats_df):
        """Display the scraped game stats (e.g., from the advanced box score) at the top of the report."""
        print("Displaying game stats at the top of the report:")
        print(game_stats_df)

    def save_as_json(self, path='output_reports/scouting_report.json'):
        # Convert keys to str to ensure JSON compatibility
        report_str_keys = {str(k): v for k, v in self.report.items()}
        
        with open(path, 'w') as f:
            json.dump(report_str_keys, f, indent=4)

    def save_as_pdf(self, path='output_reports/scouting_report.pdf', title="SCOUTING REPORT", logo_path=None, game_stats_df=None):
        os.makedirs(os.path.dirname(path), exist_ok=True)

        c = canvas.Canvas(path, pagesize=letter)
        width, height = letter

        # --- Margin Settings ---
        TOP_MARGIN = 60
        BOTTOM_MARGIN = 50
        LEFT_MARGIN = 50
        RIGHT_MARGIN = 50
        MARGIN_BUFFER = 20  # Buffer space before bottom
        PLAYER_BLOCK_HEIGHT = 120  # Height of each player block, including the margin
        PLAYER_BLOCK_SPACING = 60  # Space between player blocks

        # --- SVG LOGO POSITIONING SETTINGS ---
        logo_x = width - 120  # Horizontal position from left
        logo_y = height - 70  # Vertical position from bottom

        if logo_path and os.path.exists(logo_path):
            if logo_path.lower().endswith(".svg"):
                drawing = svg2rlg(logo_path)

                scale = 0.15
                drawing.width *= scale
                drawing.height *= scale
                drawing.scale(scale, scale)

                renderPDF.draw(drawing, c, logo_x, logo_y)
            else:
                logo_width, logo_height = 100, 50  # Default for raster logos
                c.drawImage(logo_path, 50, height - 50 - logo_height, logo_width, logo_height)

        # --- Title ---
        c.setFont("Helvetica-Bold", 16)
        c.setFillColor(colors.HexColor("#3478F8"))
        text_width = c.stringWidth(title, "Helvetica-Bold", 16)
        title_x = (width - text_width) / 2
        title_y = height - TOP_MARGIN
        c.drawString(title_x, title_y, title)
        c.setFillColor(colors.black)

        # --- Horizontal Rule ---
        line_y = title_y - 20  # Position of the line
        c.setStrokeColor(colors.HexColor("#F68718"))
        c.setLineWidth(1.5)
        c.line(LEFT_MARGIN, line_y, width - RIGHT_MARGIN, line_y)

        # Set initial Y position after title and rule
        y = line_y - MARGIN_BUFFER  # Starting Y position, buffer after horizontal line

        # --- Game Stats ---
        if game_stats_df is not None:
            c.setFont("Helvetica", 10)
            c.setFillColor(colors.black)
            c.drawString(LEFT_MARGIN, y, "Game Stats (Advanced Box Score):")
            y -= 18

            # Flattening multi-level columns for easier access
            game_stats_df.columns = ['_'.join(col).strip() for col in game_stats_df.columns.values]

            # Display cleaned game stats (advanced box score) in tabular format
            column_widths = [100, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50]  # Example column widths
            header = list(game_stats_df.columns)
            
            # Draw table header
            c.setFont("Helvetica-Bold", 10)
            for i, header_name in enumerate(header):
                c.drawString(LEFT_MARGIN + sum(column_widths[:i]), y, header_name)
            y -= 15

            # Draw table rows
            c.setFont("Helvetica", 10)
            for index, row in game_stats_df.iterrows():
                for i, col in enumerate(header):
                    c.drawString(LEFT_MARGIN + sum(column_widths[:i]), y, str(row[col]))
                y -= 12
                if y < BOTTOM_MARGIN:
                    c.showPage()  # Start a new page if space runs out
                    c.setFont("Helvetica", 10)
                    y = height - TOP_MARGIN  # Reset Y to top of new page
            y -= 10  # Extra space after game stats section

        # --- Player Stats ---
        c.setFont("Helvetica", 12)
        for player_id, stats in self.report.items():
            if player_id == "TEAM_AVERAGES":
                continue

            # Check if there is enough space for the player block, if not start a new page
            if y - PLAYER_BLOCK_HEIGHT < BOTTOM_MARGIN:
                c.showPage()  # Start a new page
                c.setFont("Helvetica", 12)
                y = height - TOP_MARGIN  # Reset Y to the top of the new page

            # Draw a light grey block background for each player
            c.setFillColor(colors.HexColor("#f0f0f0"))  # Light grey
            c.setStrokeColor(colors.HexColor("#3478F8"))
            c.rect(LEFT_MARGIN, y - PLAYER_BLOCK_HEIGHT, width - LEFT_MARGIN - RIGHT_MARGIN, PLAYER_BLOCK_HEIGHT, fill=1)  # Draw the rectangle

            # Player Name
            c.setFont("Helvetica-Bold", 14)
            c.setFillColor(colors.black)
            c.drawString(LEFT_MARGIN + 10, y - 20, f"Player {player_id}:")
            y -= 40  # Adjusting Y for player stats

            # Player stats
            c.setFont("Helvetica", 12)
            if "average_speed" in stats:
                c.drawString(LEFT_MARGIN + 10, y, f"Average Speed: {stats['average_speed']} km/h")
            if "total_distance" in stats:
                c.drawString(LEFT_MARGIN + 200, y, f"Total Distance: {stats['total_distance']} m")
            if "frames_present" in stats:
                c.drawString(LEFT_MARGIN + 400, y, f"Frames: {stats['frames_present']}")
            y -= 18

            if "activity_level" in stats:
                c.drawString(LEFT_MARGIN + 10, y, f"Activity Level: {stats['activity_level']}")
                y -= 18

            # Notes display
            if "notes" in stats and stats["notes"]:
                notes_line = f"Notes: {', '.join(stats['notes'])}"
                c.drawString(LEFT_MARGIN + 10, y, notes_line)
                y -= 18

            # Add space before the next block
            y -= PLAYER_BLOCK_SPACING  # Add vertical space between blocks

        # --- Team Averages ---
        if "TEAM_AVERAGES" in self.report:
            c.showPage()
            c.setFont("Helvetica-Bold", 16)
            c.drawString(LEFT_MARGIN, height - TOP_MARGIN, "Team Averages")

            team_stats = self.report["TEAM_AVERAGES"]
            c.setFont("Helvetica", 12)
            y = height - TOP_MARGIN - 50
            if "average_speed" in team_stats:
                c.drawString(LEFT_MARGIN, y, f"Average Speed: {team_stats['average_speed']} km/h")
                y -= 20
            if "average_distance" in team_stats:
                c.drawString(LEFT_MARGIN, y, f"Average Distance: {team_stats['average_distance']} m")

        c.save()
