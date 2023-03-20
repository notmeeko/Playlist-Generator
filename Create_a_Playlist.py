"""This program will create a music playlist based on a given artist or genre."""

import spotify

def generate_playlist(token, playlist_length, playlist_type):
    """Generates a playlist based on the user's input of playlist type, playlist length and artist/genre.

    Arguments:
        token (str): A valid Spotify access token.
        playlist_length (int): The number of songs to include in the playlist.
        playlist_type (str): The type of playlist to generate. Must be 'artist' or 'genre'.

    Returns:
        None
    """
    if playlist_type == 'artist':
        artist = input("Enter an artist: ")
        artist_id = spotify.get_artist_id(token, artist)
        if artist_id == None:
            return None
        user_songs = spotify.get_songs_by_artists(token, artist_id)
        similar_artists = spotify.get_related_artists(token, artist_id)
        print(f"\nTop {playlist_length} songs by {artist} and similar artists:")
        playlist = []
        for i, similar_artist in enumerate(similar_artists):
            #Limit to 10 similar artists
            if i == 10:
                break
            #Get songs by the similar artist
            songs = spotify.get_songs_by_artists(token, similar_artist['id'])
            #Add the songs to the playlist
            playlist.extend(songs)
        #Add songs by the artist
        playlist = user_songs + playlist
        #Sort the playlist by popularity
        playlist = sorted(playlist, key=lambda k: k['popularity'], reverse=True)
        #Print the playlist
        playlistName = f"{artist}_playlist.txt"
        for i, song in enumerate(playlist[:playlist_length]):
            print(f"{i + 1}. {song['name']} by {song['artists'][0]['name']}")
        print(f"\nYou can also find your playlist in {artist}_playlist.txt.")
        #Write playlist into new text file
        with open(f"{artist}_playlist.txt", "w") as f:
            f.write(f"Top {playlist_length} songs by {artist} and similar artists:\n")
            for i, song in enumerate(playlist[:playlist_length]):
                f.write(f"{i + 1}. {song['name']} by {song['artists'][0]['name']}\n")
    elif playlist_type == 'genre':
        genre = input("Enter a genre: ")
        songs = spotify.get_songs_by_genre(token, genre)
        if songs == None:
            return None
        print(f"\nTop {playlist_length} songs in {genre}:")
        playlistName = f"{genre}_playlist.txt"
        for i, song in enumerate(songs[:playlist_length]):
            print(f"{i + 1}. {song['name']} by {song['artists'][0]['name']}")
        print(f"\nYou can also find your playlist in {genre}_playlist.txt.")
        #Write playlist into new text file
        with open(f"{genre}_playlist.txt", "w") as f:
            f.write(f"Top {playlist_length} songs in {genre}:\n")
            for i, song in enumerate(songs[:playlist_length]):
                f.write(f"{i + 1}. {song['name']} by {song['artists'][0]['name']}\n")
    return playlistName

class playlistDetails():

    def __init__(self, name, length, playlistType):
        self.name = name
        self.length = length
        self.playlistType = playlistType

    def playlistInfo(self):
        print("\nSpotify Playlist Info:")
        print(f"\n\tPlaylist File Name: {self.name}")
        print(f"\tPlaylist Length: {self.length}")
        print(f"\tPlaylist Type: By {self.playlistType}\n")
        
def main():
    """Generate a Spotify playlist based on user input"""
    while True:
        while True:
            try:
                playlist_length = int(input("\nEnter the playlist length (1-50): "))
                if playlist_length > 0 and playlist_length <= 50:
                    break
                print("Please enter a number between 1 and 50.")
            except ValueError:
                print("Invalid input. Please enter an integer.")
        while True:
            playlist_type = input("Enter the playlist type (artist or genre): ").lower()
            if playlist_type not in ['artist', 'genre']:
                print("Invalid playlist type. Please enter 'artist' or 'genre'.")
            else:
                break
    
        #Generate playlist based on user input
        token = spotify.get_token()
        playlist = generate_playlist(token, playlist_length, playlist_type)
        if playlist == None:
            print("No results found. Your playlist was not generated.")
        else:
            viewPlaylistInfo = input("\nWould you like to view your recent Playlist Details? Yes or No? ")

            if viewPlaylistInfo.lower() == "yes":
                playlist = playlistDetails(f"{playlist}", f"{playlist_length}", f"{playlist_type}", )
                playlist.playlistInfo()

        another_playlist = input("\nWould you like to make another playlist? Yes or No? ")
        if another_playlist.lower() != "yes":
            break

if __name__ == '__main__':
    main()
