#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
from flask import (render_template, request,
                   Response, flash, redirect, url_for, jsonify, abort)
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from datetime import datetime
from sqlalchemy import func, sql
from models import app, db, Venue, Artist, Shows
import sys


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
    # Done: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.

    # Grapping each city state compination from venue table
    city_states = db.session.query(
        Venue.city,
        Venue.state
    ).group_by(Venue.city, Venue.state
               ).all()

    # Subquery to get upcoming shows
    # and dummy column to help count the number of shows for each venue
    sub_query = db.session.query(
        Shows.venue_id,
        sql.expression.bindparam("one", 1)
    ).filter(Shows.start_time > datetime.now()).subquery()

    # Get venues data and number of shows
    venues = db.session.query(
        Venue.id,
        Venue.name,
        Venue.city,
        Venue.state,
        func.sum(sub_query.c.one).label('shows')
    ).outerjoin(sub_query, sub_query.c.venue_id == Venue.id
                ).group_by(Venue.id, Venue.name, Venue.city, Venue.state
                           ).all()
    # print(venues)

    # Prepare the data object with the same structure
    data = [{"city": city,
             "state": state,
             "venues": [{
                 "id": venue.id,
                 "name": venue.name,
                 "num_upcoming_shows": 0 if venue.shows is None else venue.shows
             } for venue in venues if (venue.city == city and venue.state == state)]} for city, state in city_states]
    # print(data)

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # Done: implement search on venues with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

    search_term = request.form.get('search_term', '')
    # Subquery to get upcoming shows
    # and dummy column to help count the number of shows for each venue
    sub_query = db.session.query(
        Shows.venue_id,
        sql.expression.bindparam("one", 1)
    ).filter(Shows.start_time > datetime.now()).subquery()

    # Get venues data and number of shows
    venues = db.session.query(
        Venue.id,
        Venue.name,
        func.sum(sub_query.c.one).label('shows')
    ).outerjoin(sub_query, sub_query.c.venue_id == Venue.id
                ).group_by(Venue.id, Venue.name
                           ).having(Venue.name.ilike(f'%{search_term}%')).all()
    print(venues)
    # venues = db.session.query(Venue).filter(Venue.name.ilike(f'%{search_term}%')).all()
    # print(venues)
    response = {
        "count": len(venues),
        "data": [{
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": 0 if venue.shows is None else venue.shows
        } for venue in venues]
    }
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # Done: replace with real venue data from the venues table, using venue_id

    # Get venue by venue_id
    venue = Venue.query.get(venue_id)

    # Get the past shows for this venue
    past_shows = db.session.query(
        Shows.artist_id,
        Artist.name,
        Artist.image_link,
        Shows.start_time
    ).join(Shows, Shows.artist_id == Artist.id
           ).filter(Shows.start_time < datetime.now(), Shows.venue_id == venue_id
                    ).all()

    # Get the upcoming shows for this venue
    upcoming_shows = db.session.query(
        Shows.artist_id,
        Artist.name,
        Artist.image_link,
        Shows.start_time
    ).join(Shows, Shows.artist_id == Artist.id
           ).filter(Shows.start_time > datetime.now(), Shows.venue_id == venue_id
                    ).all()

    # Prepare the data object
    data = {
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
        "past_shows": [{
            "artist_id": show.artist_id,
            "artist_name": show.name,
            "artist_image_link": show.image_link,
            "start_time": str(show.start_time)
        } for show in past_shows],
        "upcoming_shows": [{
            "artist_id": show.artist_id,
            "artist_name": show.name,
            "artist_image_link": show.image_link,
            "start_time": str(show.start_time)
        } for show in upcoming_shows],
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
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
    try:
        # Done: insert form data as a new Venue record in the db, instead
        # Done: modify data to be the data object returned from db insertion
        form = VenueForm(request.form)
        venue = Venue()
        form.populate_obj(venue)
        db.session.add(venue)
        db.session.commit()
        # on successful db insert, flash success
        flash('Venue ' + venue.name + ' was successfully listed!')
    except Exception:
        db.session.rollback()
        # Done: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        flash('An error occurred. Venue ' +
              venue.name + ' could not be listed.')
        print(sys.exc_info())
    finally:
        db.session.close()
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # Done: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    error = False
    try:
        venue = Venue.query.get(venue_id)
        venue_name = venue.name
        db.session.delete(venue)
        db.session.commit()
        flash('Venue ' + venue_name + ' was successfully deleted!')
    except Exception:
        db.session.rollback()
        error = True
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
        return jsonify({'success': True})

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    # Done: replace with real data returned from querying the database
    artists = db.session.query(
        Artist.id,
        Artist.name
    ).all()
    data = [{
        "id": artist.id,
        "name": artist.name
    } for artist in artists]
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # Done: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    search_term = request.form.get('search_term', '')
    # Subquery to get upcoming shows
    # and dummy column to help count the number of shows for each venue
    sub_query = db.session.query(
        Shows.artist_id,
        sql.expression.bindparam("one", 1)
    ).filter(Shows.start_time > datetime.now()).subquery()

    # Get venues data and number of shows
    artists = db.session.query(
        Artist.id,
        Artist.name,
        func.sum(sub_query.c.one).label('shows')
    ).outerjoin(sub_query, sub_query.c.artist_id == Artist.id
                ).group_by(Artist.id, Artist.name
                           ).having(Artist.name.ilike(f'%{search_term}%')).all()
    print(venues)
    # venues = db.session.query(Venue).filter(Venue.name.ilike(f'%{search_term}%')).all()
    # print(venues)
    response = {
        "count": len(artists),
        "data": [{
            "id": artist.id,
            "name": artist.name,
            "num_upcoming_shows": 0 if artist.shows is None else artist.shows
        } for artist in artists]
    }
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    # Done: replace with real venue data from the venues table, using venue_id
    # Get the artist data by artist_id
    artist = Artist.query.get(artist_id)
    # Get the past shows for this venue
    past_shows = db.session.query(
        Shows.venue_id,
        Venue.name,
        Venue.image_link,
        Shows.start_time
    ).join(Shows, Shows.venue_id == Venue.id
           ).filter(Shows.start_time < datetime.now(), Shows.artist_id == artist_id
                    ).all()

    # Get the upcoming shows for this venue
    upcoming_shows = db.session.query(
        Shows.venue_id,
        Venue.name,
        Venue.image_link,
        Shows.start_time
    ).join(Shows, Shows.venue_id == Venue.id
           ).filter(Shows.start_time > datetime.now(), Shows.artist_id == artist_id
                    ).all()

    # Prepare the data object
    data = {
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
        "past_shows": [{
            "venue_id": show.venue_id,
            "venue_name": show.name,
            "venue_image_link": show.image_link,
            "start_time": str(show.start_time)
        } for show in past_shows],
        "upcoming_shows": [{
            "venue_id": show.venue_id,
            "venue_name": show.name,
            "venue_image_link": show.image_link,
            "start_time": str(show.start_time)
        } for show in upcoming_shows],
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
    }
    return render_template('pages/show_artist.html', artist=data)


@app.route('/artist/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
    # Done: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    error = False
    try:
        artist = Artist.query.get(artist_id)
        artist_name = artist.name
        print(artist)
        db.session.delete(artist)
        db.session.commit()
        flash('Venue ' + artist_name + ' was successfully deleted!')
    except Exception:
        db.session.rollback()
        error = True
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
        return jsonify({'success': True})

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.get(artist_id)
    artist = {
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
        "image_link": artist.image_link
    }
    # Done: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # Done: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    form = request.form
    try:
        artist = Artist.query.get(artist_id)
        artist.name = form['name']
        artist.city = form['city']
        artist.state = form['state']
        artist.phone = form['phone']
        artist.image_link = None if form['image_link'] == '' else form['image_link']
        artist.facebook_link = None if form['facebook_link'] == '' else form['facebook_link']
        artist.genres = request.form.getlist('genres')
        artist.website = None if form['website'] == '' else form['website']
        artist.seeking_venue = True if request.form.get(
            'seeking_venue', False) == 'y' else False
        artist.seeking_description = None if form['seeking_description'] == '' else form['seeking_description']
        db.session.add(artist)
        db.session.commit()
        # on successful db insert, flash success
        flash('artist ' + artist.name + ' was successfully edited!')
    except Exception:
        db.session.rollback()
        # Done: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. artist ' + data.name + ' could not be listed.')
        flash('An error occurred. artist ' +
              artist.name + ' could not be edited.')
        print(sys.exc_info())
    finally:
        db.session.close()
    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.get(venue_id)
    venue = {
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
        "image_link": venue.image_link
    }
    # Done: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # Done: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    try:
        form = request.form
        venue = Venue.query.get(venue_id)
        venue.name = form['name']
        venue.city = form['city']
        venue.state = form['state']
        venue.address = form['address']
        venue.phone = form['phone']
        venue.image_link = None if form['image_link'] == '' else form['image_link']
        venue.facebook_link = None if form['facebook_link'] == '' else form['facebook_link']
        venue.genres = request.form.getlist('genres')
        venue.website = None if form['website'] == '' else form['website']
        venue.seeking_talent = True if request.form.get(
            'seeking_talent', False) == 'y' else False
        venue.seeking_description = None if form['seeking_description'] == '' else form['seeking_description']
        db.session.add(venue)
        db.session.commit()
        # on successful db insert, flash success
        flash('Venue ' + venue.name + ' was successfully listed!')
    except Exception:
        db.session.rollback()
        # Done: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        flash('An error occurred. Venue ' +
              venue.name + ' could not be listed.')
        print(sys.exc_info())
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
    try:
        # called upon submitting the new artist listing form
        # Done: insert form data as a new Venue record in the db, instead
        # Done: modify data to be the data object returned from db insertion
        form = ArtistForm(request.form)
        artist = Artist()
        form.populate_obj(artist)
        db.session.add(artist)
        db.session.commit()
        # on successful db insert, flash success
        flash('artist ' + fartist.name + ' was successfully listed!')
    except Exception:
        db.session.rollback()
        # Done: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. artist ' + data.name + ' could not be listed.')
        flash('An error occurred. artist ' +
              artist.name + ' could not be listed.')
        print(sys.exc_info())
    finally:
        db.session.close()
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # Done: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    shows = db.session.query(
        Shows.venue_id,
        Venue.name.label('venue_name'),
        Artist.id,
        Artist.name.label('artist_name'),
        Artist.image_link,
        Shows.start_time
    ).join(Shows, Shows.venue_id == Venue.id
           ).join(Artist, Shows.artist_id == Artist.id
                  ).filter(Shows.start_time > datetime.now()
                           ).all()
    data = [{
        "venue_id": show.venue_id,
        "venue_name": show.venue_name,
        "artist_id": show.id,
        "artist_name": show.artist_name,
        "artist_image_link": show.image_link,
        "start_time": str(show.start_time)
    } for show in shows]
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # Done: insert form data as a new Show record in the db, instead
    try:
        form = ShowForm(request.form)
        show = Shows()
        form.populate_obj(show)
        db.session.add(show)
        db.session.commit()
        # on successful db insert, flash success
        flash('Show was successfully listed!')
    except Exception:
        db.session.rollback()
        # Done: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        flash('An error occurred. Show could not be listed.')
        print(sys.exc_info())
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
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
    app.run(debug=True)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
