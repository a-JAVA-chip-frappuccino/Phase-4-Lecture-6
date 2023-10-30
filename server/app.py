from flask import request, make_response

from flask_restful import Api, Resource

from werkzeug.exceptions import NotFound

from config import app

from models import db, User, NationalPark, UserVisitedPark

api = Api(app)

# unique error message upon nonexistent server-side route
@app.errorhandler(NotFound)
def route_not_found(e):
    response = make_response(
        "That route does not exist!",
        404
    )
    
    return response

@app.route('/')
def home():
    return ""

@app.route('/users', methods = ['GET', 'POST'])
def users():

    if request.method == 'GET':
        users = User.query.all()
    
        users_dict = [user.to_dict(rules = ('-user_visited_park', '-password')) for user in users]

        response = make_response(
            users_dict,
            200
        )

    elif request.method == 'POST':
        form_data = request.get_json()

        try:

            new_user_obj = User(
                username = form_data['username'],
                password = form_data['password']
            )

            db.session.add(new_user_obj)

            db.session.commit()

            response = make_response(
                new_user_obj.to_dict(),
                201
            )

        except ValueError:

            response = make_response(
                { "Username must be between 4 and 14 characters, inclusive!" : None },
                403
            )

            return response

    return response

class NationalParks(Resource):

    def get(self):
        national_parks = NationalPark.query.all()

        national_parks_dict = [national_park.to_dict() for national_park in national_parks]

        response = make_response(
            national_parks_dict,
            200
        )

        return response
    
api.add_resource(NationalParks, '/national_parks')

'''
@app.route('/national_parks', methods = ['GET'])
def national_parks():
    national_parks = NationalPark.query.all()

    national_parks_dict = [national_park.to_dict() for national_park in national_parks]

    response = make_response(
        national_parks_dict,
        200
    )

    return response
'''

@app.route('/users/<int:id>', methods = ['GET', 'PATCH'])
def user_by_id(id):
    user = User.query.filter_by(id = id).first()
    # user = User.query.filter(User.id == id).first()

    ''' # version with None statement
    
        if user == None:
            
            response = make_response(
                { "User not found!" : None },
                404
            )

            return response

    '''

    if user:

        if request.method == 'GET':
            user_dict = user.to_dict(rules = ('-user_visited_park', ))

            response = make_response(
                user_dict,
                200
            )

        elif request.method == 'PATCH':
            form_data = request.get_json()

            try:

                for attr in form_data:
                    setattr(user, attr, form_data.get(attr))

                db.session.commit()

                response = make_response(
                    user.to_dict(),
                    201
                )

            except ValueError:

                response = make_response(
                    { "Username must be between 4 and 14 characters, inclusive!" : None },
                    403
                )

                return response

    else:

        response = make_response(
            { "User not found!" : None },
            404
        )

    return response

    # return make_response(user.to_dict(), 200)

@app.route('/national_parks/<int:id>', methods = ['DELETE'])
def national_park_by_id(id):
    park = NationalPark.query.filter_by(id = id).first()
    # park = NationalPark.query.filter(NationalPark.id == id).first()

    if park:

        associated_visits = UserVisitedPark.query.filter(UserVisitedPark.park_id == id).all()

        for associated_visit in associated_visits:
            db.session.delete(associated_visit)

        db.session.delete(park)

        db.session.commit()

        response = make_response(
            {},
            202
        )

    else:

        response = make_response(
            { "NationalPark not found!" : None },
            404
        )

    return response

if __name__ == '__main__':
    app.run(port = 5555, debug = True)