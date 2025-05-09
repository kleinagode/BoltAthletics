from sklearn.cluster import KMeans

class TeamAssigner:
    def __init__(self):
        self.team_colors = {}
        self.player_team_dict = {}

    def get_clustering_model(self, img):

        # Reshape into 2d
        img_2d = img.reshape(-1,3)

        # Do K-Means with 2 clusters
        kmeans = KMeans(n_clusters=2, init="k-means++", n_init=1)
        kmeans.fit(img_2d)

        return kmeans
    

    def get_player_color(self, frame, bbox):
        img = frame[int(bbox[1]):int(bbox[3]), int(bbox[0]):int(bbox[2])]

        top_half_img = img[int(img.shape[0]*0.10):int(img.shape[0]*0.60), int(img.shape[1]*0.25):int(img.shape[1]*0.75)]

        # Get Clustering Model
        kmeans = self.get_clustering_model(top_half_img)

        # Get labels
        labels = kmeans.labels_

        # Reshape
        clustered_image = labels.reshape(top_half_img.shape[0], top_half_img.shape[1])

        # Get player cluster
        corner_clusters = [clustered_image[0,0], clustered_image[0,-1],clustered_image[-1,0],clustered_image[-1,-1]]
        non_player_cluster = max(set(corner_clusters), key=corner_clusters.count)
        player_cluster = 1 - non_player_cluster

        player_color = kmeans.cluster_centers_[player_cluster]

        return player_color

    def assign_team_color(self, frame, player_detections):
        
        player_colors = []
        for _, player_detection in player_detections.items():
            bbox = player_detection['bbox']
            player_color = self.get_player_color(frame, bbox)
            player_colors.append(player_color)

        kmeans = KMeans(n_clusters=2, init="k-means++", n_init=1)
        kmeans.fit(player_colors)

        self.kmeans = kmeans

        # Color for each team
        self.team_colors[1] = kmeans.cluster_centers_[0]
        self.team_colors[2] = kmeans.cluster_centers_[1]


    def get_player_team(self, frame, player_bbox, player_id):

        if player_id in self.player_team_dict:
            return self.player_team_dict[player_id]
        
        player_color = self.get_player_color(frame, player_bbox)

        team_id = self.kmeans.predict(player_color.reshape(1,-1))[0]
        team_id+=1 # 1 or 0

        self.player_team_dict[player_id] = team_id
        
        return team_id