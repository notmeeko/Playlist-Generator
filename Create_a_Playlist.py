"""This program will create a music playlist based on a given artist or genre."""


import base64
from requests import post, get
import json


#Spotify client ID and secret key for authentication
client_id = "bbff0e095ce94643a1c8d1136824dbfa"
client_secret = "0efd5f03128e480c9213e99d44947425"

def get_token():
    """Obtains an access token from the Spotify API using client credentials authentication."""
    #Encode the client ID and secret key as base64
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    #Send a POST request to the Spotify API to obtain an access token
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token

def get_auth_header(token):
    """Generates the authorization header required to access Spotify API endpoints.
    
    Arguments:
        token (str): A string containing a valid access token
    
    Returns:
        dict: A dictionary containing the authorization header.
    """
    return {"Authorization": "Bearer " + token}

def search_for_artist(token, artist_name):
    """Searches for an artist in the Spotify API and returns information about the first result.

    Arguments:
        token (str): The access token for the Spotify API.
        artist_name (str): The name of the artist to search for.

    Returns:
        dict: A dictionary containing information about the first artist that matches the search query.
    """
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={artist_name}&type=artist&limit=1"

    query_url = url + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)["artists"]["items"]

    if len(json_result) == 0:
        print("No artist with this name exists...")
        return None
    
    return json_result[0]

def get_artist_id(token, artist):
    """Returns the Spotify ID of the artist based on the provided artist name.

    Arguments:
        token (str): A valid Spotify access token.
        artist (str): The name of the artist to search for.

    Returns:
        str: The Spotify ID of the artist.
    """
    result = search_for_artist(token, f"{artist}")
    if result == None:
        return None
    artist_id = (result["id"])
    
    return artist_id

def get_artist_name(token, artist):
    """Gets the name of the first artist in Spotify's search results for the given artist name.

    Arguments:
        token (str): A Spotify access token.
        artist (str): The name of the artist to search for.

    Returns:
        str: The name of the first artist in Spotify's search results for the given artist name.
    """
    result = search_for_artist(token, f"{artist}")
    artist_name = (result["name"])
    return artist_name

def get_songs_by_artists(token, artist_id):
    """
    Returns a list of the top tracks of an artist on Spotify, given the artist's ID.

    Arguments:
    token (str): A valid Spotify access token.
    artist_id (str): The unique Spotify ID of the artist whose top tracks are to be retrieved.

    Returns:
    list: A list of dictionaries containing information about the top tracks of the specified artist on Spotify. Each dictionary contains information such as the track name, album name, and preview URL.
    """
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=US"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)["tracks"]
    return json_result

def get_related_artists(token, artist_id):
    """
    Given a Spotify access token and an artist ID, this function returns a list of related artists.

    Arguments:
    token (str): A valid Spotify access token.
    artist_id (str): The Spotify ID of the artist to find related artists for.

    Returns:
    list: A list of related artists, represented as dictionaries containing information about each artist.
    """
    url = f"https://api.spotify.com/v1/artists/{artist_id}/related-artists"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)["artists"]
    return json_result

def top_songs_of_related_artists(token, artist_id):
    """
    Returns a list of top songs by related artists to the specified artist.

    Arguments:
    token (str): A valid access token for the Spotify API.
    artist_id (str): The unique identifier for the artist.

    Returns:
    list: A list of top songs by related artists to the specified artist.
    """
    songs = get_songs_by_artists(token, artist_id)
    listOfSongs = []
    for i, song in enumerate(songs):
        listOfSongs.append(song['name'])
    return listOfSongs

def get_songs_by_genre(token, genre):
    """
    Searches the Spotify API for tracks with a given genre and returns a list of track information.
    
    Arguments:
        token (str): string containing a valid access token for the Spotify API.
        genre (str): string containing the name of the genre to search for.
    
    Returns:
        list: A list of track information that matches the given genre search criteria.
    """
    url = f"https://api.spotify.com/v1/search?q=genre%3A{genre}&type=track&limit=50"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)["tracks"]["items"]
    if json_result == []:
        return None
    return json_result

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
        artist_id = get_artist_id(token, artist)
        if artist_id == None:
            return None
        user_songs = get_songs_by_artists(token, artist_id)
        similar_artists = get_related_artists(token, artist_id)
        print(f"\nTop {playlist_length} songs by {artist} and similar artists:")
        playlist = []
        for i, similar_artist in enumerate(similar_artists):
            #Limit to 10 similar artists
            if i == 10:
                break
            #Get songs by the similar artist
            songs = get_songs_by_artists(token, similar_artist['id'])
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
        songs = get_songs_by_genre(token, genre)
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
    else:
        #Invalid playlist type
        print("Invalid playlist type. Please enter 'artist' or 'genre'.")
    return playlistName

class playlistDetails():

    def __init__(self, name, length, playlistType):
        self.name = name
        self.length = length
        self.playlistType = playlistType

    def playlistInfo(self):
        print("\nSpotify Playlist Info:")
        print(f"\n    Playlist File Name: {self.name}")
        print(f"    Playlist Length: {self.length}")
        print(f"    Playlist Type: By {self.playlistType}\n")
        
def main():
    """Generate a Spotify playlist based on user input"""
    while True:
        token = get_token()
        while True:
            try:
                playlist_length = int(input("\nEnter the playlist length (Max 50): "))
                if playlist_length <= 50 and playlist_length > 0:
                    break
                print("Maximum of 50 songs is allowed.")
            except ValueError:
                print("Invalid input. Please enter a number.")
        while True:
            playlist_type = input("Enter the playlist type (artist or genre): ")
            if playlist_type not in ['artist', 'genre']:
                print("Invalid playlist type. Please enter 'artist' or 'genre'.")
            else:
                break
    
        #Generate playlist based on user input
        playlist = generate_playlist(token, playlist_length, playlist_type)
        if playlist == None:
            print("No results found. Your playlist was not generated.")
        else:
            viewPlaylistInfo = input("\nWould you like to view your recent Playlist Details? Yes or No? ")

            if viewPlaylistInfo == 'yes' or viewPlaylistInfo == 'Yes':
                playlist = playlistDetails(f"{playlist}", f"{playlist_length}", f"{playlist_type}", )
                playlist.playlistInfo()

        another_playlist = input("\nWould you like to make another playlist? Yes or No? ")
        if another_playlist.lower() == "no":
            break

if __name__ == '__main__':
    main()
