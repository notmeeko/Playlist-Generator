"""This program will create a music playlist based on a given artist or genre."""


import base64
from requests import post, get
import json


#Spotify client ID and secret key for authentication
client_id = "bbff0e095ce94643a1c8d1136824dbfa"
client_secret = "0efd5f03128e480c9213e99d44947425"

#Function to get an access token for the Spotify Web API
def get_token():
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

#Function to generate the authorization header for API requests
def get_auth_header(token):
    return {"Authorization": "Bearer " + token}

#Function to search for an artist by name and return their ID
def search_for_artist(token, artist_name):
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

#Function to get an artist's ID from their name
def get_artist_id(token, artist):
    result = search_for_artist(token, f"{artist}")
    artist_id = (result["id"])
    return artist_id

#Function to get an artist's name from their ID
def get_artist_name(token, artist):
    result = search_for_artist(token, f"{artist}")
    artist_name = (result["name"])
    return artist_name

#Function to get an artist's top tracks by ID
def get_songs_by_artists(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=US"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)["tracks"]
    return json_result

#Function to get related artists by ID
def get_related_artists(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/related-artists"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)["artists"]
    return json_result

#Function to get top songs of related artists
def top_songs_of_related_artists(token, artist_id):
    songs = get_songs_by_artists(token, artist_id)
    listOfSongs = []
    for i, song in enumerate(songs):
        listOfSongs.append(song['name'])
    return listOfSongs

#Function to get songs by genre
def get_songs_by_genre(token, genre):
    url = f"https://api.spotify.com/v1/search?q=genre%3A{genre}&type=track&limit=50"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)["tracks"]["items"]
    return json_result

def generate_playlist(token, playlist_length, playlist_type):
    #Check playlist type
    if playlist_type == 'artist':
        #Get artist name from user input
        artist = input("Enter an artist: ")
        #Get artist ID using the get_artist_id() function
        artist_id = get_artist_id(token, artist)  # Add token argument here
        #Get top songs by the artist using the get_songs_by_artists() function
        user_songs = get_songs_by_artists(token, artist_id)
        #Print top 10 songs by the artist
        #print(f"\nTop 10 songs by {get_artist_name(token, artist)}:")
        #for i, song in enumerate(songs[:playlist_length]):
            #print(f"{i + 1}. {song['name']}")
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
        #Sort the playlist by popularity
        #playlist = sorted(playlist, key=lambda k: k['popularity'], reverse=True)
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
    #Get token
    token = get_token()
    
    #Get user input for playlist length and type
    playlist_length = int(input("Enter the playlist length: "))
    playlist_type = input("Enter the playlist type (artist or genre): ")
    
    #Generate playlist based on user input
    generate_playlist(token, playlist_length, playlist_type)

if __name__ == '__main__':
    main()
