#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
from unicodedata import name
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from sqlalchemy import func
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db, compare_type=True)

# TODO: connect to a local postgresql database

from models import *

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  areas_list = db.session.query(Venue.city, Venue.state).distinct()
  data = []
  for area in areas_list:
    venues_in_area = Venue.query.filter_by(state=area.state, city=area.city).order_by(Venue.state, Venue.city)
    venue_list = []
    for venue in venues_in_area:
      upcoming_shows = db.session.query(Show).filter(Show.venue_id==venue.id).filter(Show.start_time>datetime.now()).all()
      venue_list.append({
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": len(upcoming_shows)
      })
    data.append({
      "city": area.city,
      "state": area.state,
      "venues": venue_list
    })
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  data = []
  response = {}
  search_term = request.form.get('search_term', '')
  venues = db.session.query(Venue).filter(Venue.name.ilike('%' + search_term + '%')).all()
  count = len(venues)
  for venue in venues:
    num_upcoming_shows = len(db.session.query(Show).filter(Show.venue_id==venue.id).filter(Show.start_time>datetime.now()).all())
    data.append({
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": num_upcoming_shows
    })
  response={
    "count": count,
    "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  data = {}
  upcoming_shows = []
  past_shows = []
  venue = db.session.query(Venue).filter(Venue.id==venue_id).first()
  upcoming_shows_data = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time>=datetime.now()).all()
  past_shows_data = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time<datetime.now()).all()
  for show in upcoming_shows_data:
    upcoming_shows.append({
      "artist_id": show.artist_id,
      "artist_name": show.artists.name,
      "artist_image_link": show.artists.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })

  for show in past_shows_data:
    past_shows.append({
      "artist_id": show.artist_id,
      "artist_name": show.artists.name,
      "artist_image_link": show.artists.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
  })

  past_shows_count = len(past_shows)
  upcoming_shows_count = len(upcoming_shows)

  data={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": past_shows_count,
    "upcoming_shows_count": upcoming_shows_count,
  }
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm()
  venue = Venue()
  try:
    venue.name = form.name.data
    venue.city = form.city.data
    venue.state = form.state.data
    venue.address = form.address.data
    venue.phone = form.phone.data
    venue.image_link = form.image_link.data
    venue.genres = form.genres.data
    venue.facebook_link = form.facebook_link.data
    venue.website = form.website_link.data
    venue.seeking_talent = form.seeking_talent.data
    venue.seeking_description = form.seeking_description.data
    db.session.add(venue)
    db.session.commit()

    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    db.session.rollback()
  finally:
    db.session.close()
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  error = False
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
    flash('Venue ' + venue.name + ' was successfully deleted!')
  except:
    db.session.rollback()
    error = True
    flash('There was an error when deleting Venue ' + venue.name + '!')
  finally:
    db.session.close()
  if error:
    abort(500) 
  else:
    return None
  

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = []
  artists = db.session.query(Artist).order_by(Artist.name).all()
  for artist in artists:
    data.append({
      "id": artist.id,
      "name": artist.name
    })
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  data = []
  response = {}
  search_term = request.form.get('search_term', '')
  artists = db.session.query(Artist).filter(Artist.name.ilike('%' + search_term + '%')).order_by(Artist.name).all()
  count = len(artists)
  for artist in artists:
    num_upcoming_shows = len(db.session.query(Show).filter(Show.artist_id==artist.id).filter(Show.start_time>datetime.now()).all())
    data.append({
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_shows": num_upcoming_shows
    })
  response={
    "count": count,
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  data = {}
  upcoming_shows = []
  past_shows = []
  artist = db.session.query(Artist).filter(Artist.id==artist_id).first()
  upcoming_shows_data = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time>=datetime.now()).all()
  past_shows_data = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time<datetime.now()).all()
  for show in upcoming_shows_data:
    upcoming_shows.append({
      "venue_id": show.venue_id,
      "venue_name": show.venues.name,
      "venue_image_link": show.venues.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })

  for show in past_shows_data:
    past_shows.append({
      "venue_id": show.venue_id,
      "venue_name": show.venues.name,
      "venue_image_link": show.venues.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
  })

  past_shows_count = len(past_shows)
  upcoming_shows_count = len(upcoming_shows)

  data={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": past_shows_count,
    "upcoming_shows_count": upcoming_shows_count,
  }
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  form.name.data = artist.name
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.genres.data = artist.genres
  form.facebook_link.data = artist.facebook_link
  form.image_link.data = artist.image_link
  form.website_link.data = artist.website
  form.seeking_venue.data = artist.seeking_venue
  form.seeking_description.data = artist.seeking_description
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  artist = Artist.query.get(artist_id)
  form = ArtistForm()

  try:
    artist.name = form.name.data
    artist.city = form.city.data
    artist.state = form.state.data
    artist.phone = form.phone.data
    artist.genres = form.genres.data
    artist.facebook_link = form.facebook_link.data
    artist.website = form.website_link.data
    artist.image_link = form.image_link.data
    artist.seeking_venue = form.seeking_venue.data
    artist.seeking_description = form.seeking_description.data
    db.session.commit()
    flash('Artist ' + form.name.data + ': details were updated successfully!') 
  except:
    flash('An error occured while updating the details of Artist: ' + form.name.data)
    db.session.rollback()
  finally:
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

  

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  form.name.data = venue.name
  form.city.data = venue.city
  form.state.data = venue.state
  form.address.data = venue.address
  form.phone.data = venue.phone
  form.image_link.data = venue.image_link
  form.facebook_link.data = venue.facebook_link
  form.genres.data = venue.genres
  form.website_link.data = venue.website
  form.seeking_talent.data = venue.seeking_talent
  form.seeking_description.data = venue.seeking_description

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  venue = Venue.query.get(venue_id)
  form = VenueForm()
  try:
    venue.name = form.name.data
    venue.city = form.city.data
    venue.state = form.state.data
    venue.address = form.address.data
    venue.phone = form.phone.data
    venue.image_link = form.image_link.data
    venue.facebook_link = form.facebook_link.data
    venue.genres = form.genres.data
    venue.website = form.website_link.data
    venue.seeking_talent = form.seeking_talent.data
    venue.seeking_description = form.seeking_description.data
    db.session.commit()
    flash('Venue ' + form.name.data + ': details were updated successfully!') 
  except:
    flash('An error occured while updating the details of Venue: ' + form.name.data)
    db.session.rollback()
  finally:
    db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm()
  artist = Artist()
  try:
    artist.name = form.name.data
    artist.city = form.city.data
    artist.state = form.state.data
    artist.phone = form.phone.data
    artist.genres = form.genres.data
    artist.facebook_link = form.facebook_link.data
    artist.website = form.website_link.data
    artist.image_link = form.image_link.data
    artist.seeking_venue = form.seeking_venue.data
    artist.seeking_description = form.seeking_description.data
    db.session.add(artist)
    db.session.commit()
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    flash('An error occured while listing Artist: ' + form.name.data)
    db.session.rollback()
  finally:
    db.session.close()

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  shows = db.session.query(Show).all()
  data = []
  for show in shows:
    data.append({
      "venue_id": show.venue_id,
      "venue_name": db.session.query(Venue.name).filter(Venue.id==show.venue_id).first()[0],
      "artist_id": show.artist_id,
      "artist_name": db.session.query(Artist.name).filter(Artist.id==show.artist_id).first()[0],
      "artist_image_link": db.session.query(Artist.image_link).filter(Artist.id==show.artist_id).first()[0],
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })
  
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  form = ShowForm()
  show = Show()
  try:
    show.artist_id = form.artist_id.data
    show.venue_id = form.venue_id.data
    show.start_time = form.start_time.data
    db.session.add(show)
    db.session.commit()

    # on successful db insert, flash success
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    flash('Show could not be listed due to an error')
  finally:
    db.session.close()

  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
