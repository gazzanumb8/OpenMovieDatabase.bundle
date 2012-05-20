import re

def Start():
  HTTP.CacheTime = CACHE_1WEEK
  HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:12.0) Gecko/20100101 Firefox/12.0'
  HTTP.Headers['Referer'] = 'http://www.imdb.com/'

class UnofficialImdbApi(Agent.Movies):
  name = 'Unofficial IMDb API'
  languages = [Locale.Language.English]
  primary_provider = False
  contributes_to = ['com.plexapp.agents.imdb']

  def search(self, results, media, lang):
    imdb_id = media.primary_metadata.id
    results.Append(MetadataSearchResult(id=imdb_id, score=99))

  def update(self, metadata, media, lang):
    url = 'http://www.imdbapi.com/?i=%s' % metadata.id

    try:
      movie = JSON.ObjectFromURL(url, sleep=5.0)
    except:
      Log('Failed when trying to open url: ' + url)
      movie = None

    if movie is not None:
      if movie['Response'] == 'True':
        metadata.title = movie['Title']
        metadata.year = int(movie['Year'])

        if movie['Rated'] != 'N/A':
          metadata.content_rating = movie['Rated']
        else:
          metadata.content_rating = None

        if movie['Released'] != 'N/A':
          metadata.originally_available_at = Datetime.ParseDate(movie['Released']).date()
        else:
          metadata.originally_available_at = None

        metadata.genres.clear()
        if movie['Genre'] != 'N/A':
          for genre in movie['Genre'].split(','):
            metadata.genres.add(genre.strip())

        metadata.writers.clear()
        if movie['Writer'] != 'N/A':
          for writer in movie['Writer'].split(','):
            metadata.writers.add(writer.strip())

        metadata.directors.clear()
        if movie['Director'] != 'N/A':
          for director in movie['Director'].split(','):
            metadata.directors.add(director.strip())

        metadata.roles.clear()
        if movie['Actors'] != 'N/A':
          for actor in movie['Actors'].split(','):
            role = metadata.roles.new()
            role.actor = actor.strip()

        if movie['Plot'] != 'N/A':
          metadata.summary = movie['Plot']
        else:
          metadata.summary = ''

        if movie['Rating'] != 'N/A':
          metadata.rating = float(movie['Rating'])
        else:
          metadata.rating = None

        duration = 0
        try:
          runtime = re.search('([0-9]+) hrs? ([0-9]+) min', movie['Runtime'])
          duration += int(runtime.group(1)) * 60 * 60 * 1000
          duration += int(runtime.group(2)) * 60 * 1000
        except:
          pass
        if duration > 0:
          metadata.duration = duration

        if Prefs['imdb_poster']:
          try:
            poster = movie['Poster']
            fullsize = poster.split('@@')[0] + '@@._V1._SX640.jpg'
            thumb    = poster.split('@@')[0] + '@@._V1._SX100.jpg'
            if fullsize not in metadata.posters:
              p = HTTP.Request(thumb)
              metadata.posters[fullsize] = Proxy.Preview(p, sort_order=1)
          except:
            pass
        else:
          try:
            poster = movie['Poster']
            del metadata.posters[poster]
          except:
            pass

      else:
        Log('An error occured. The json response is:')
        Log(movie)