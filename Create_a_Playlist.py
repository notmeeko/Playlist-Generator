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
    #Check playlist type
    if playlist_type == 'artist':
        #Get artist name from user input
        artist = input("Enter an artist: ")
        #Get artist ID using the get_artist_id() function
        artist_id = get_artist_id(token, artist)  # Add token argument here
        #Get top songs by the artist using the get_songs_by_artists() function
        user_songs = get_songs_by_artists(token, artist_id)
        #Get related artists using the get_related_artists() function
        similar_artists = get_related_artists(token, artist_id)
        #Print top playlist_length songs by similar artists
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
        for i, song in enumerate(playlist[:playlist_length]):
            print(f"{i + 1}. {song['name']} by {song['artists'][0]['name']}")
    elif playlist_type == 'genre':
        #Get genre from user input
        genre = input("Enter a genre: ")
        #Get top songs by the genre using the get_songs_by_genre() function
        songs = get_songs_by_genre(token, genre)
        #Print top playlist_length songs in the genre
        print(f"\nTop {playlist_length} songs in {genre}:")
        for i, song in enumerate(songs[:playlist_length]):
            print(f"{i + 1}. {song['name']} by {song['artists'][0]['name']}")
    else:
        #Invalid playlist type
        print("Invalid playlist type. Please enter 'artist' or 'genre'.")

def main():
    """Generate a Spotify playlist based on user input"""
    #Get token
    token = get_token()
    
    #Get user input for playlist length and type
    playlist_length = int(input("Enter the playlist length: "))
    playlist_type = input("Enter the playlist type (artist or genre): ")
    
    #Generate playlist based on user input
    generate_playlist(token, playlist_length, playlist_type)

if __name__ == '__main__':
    main()