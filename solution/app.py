from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import hashlib
import datetime

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///countries.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)

def generate_password_hash(password):
    password_hashed = hashlib.md5(password.encode()).hexdigest()
    return password_hashed

class Countries(db.Model):
    name = db.Column(db.String(100), primary_key=True, nullable=False, unique=True)
    alpha2 = db.Column(db.String(2), nullable=False)
    alpha3 = db.Column(db.String(3), nullable=False)
    region = db.Column(db.String(100), nullable=True)
    
class User(db.Model):
    login = db.Column(db.String(30), primary_key=True, nullable=False)
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    countryCode = db.Column(db.String(2), nullable=False)
    isPublic = db.Column(db.Boolean(), nullable=False)
    phone = db.Column(db.String(), nullable=True)
    image = db.Column(db.Text, nullable=True)

    def __init__(self, login, email, password, countryCode, isPublic, phone=None, image=None):
        self.login = login
        self.email = email
        self.password = password
        self.countryCode = countryCode
        self.isPublic = isPublic
        self.phone = phone
        self.image = image

# создаем базу данных, если ее пока нет
with app.app_context():
    db.create_all()

# презенторы - функции, которые представляют модели в виде словарей
def present_country(country):
    return {
        "name": country.name,
        "alpha2": country.alpha2,
        "alpha3": country.alpha3,
        "region": country.region
    }

def present_user(user):
    return {
        "login": user.login,
        "email": user.email,
        "password": user.password,
        "countryCode": user.countryCode,
        "isPublic": user.isPublic,
        "phone": user.phone,
        "image": user.image
    }
# ендпоинты - реагируют на запросы пользователей


@app.route("/api/ping", methods=["GET"])
def send():
    return jsonify({"status": "ok"}), 200

@app.route("/api/countries", methods=["GET"])
def get_filter_by_region_countries():
    countries = Countries.query.all()
    region = request.args.get("region")
    # print(region)
    countries_descriptions = [present_country(country) for country in countries if present_country(country)["region"] == region]
    return jsonify(countries_descriptions)

@app.route("/api/countries/<alpha2>", methods=["GET"])
def get_filter_by_alpha2_countries(alpha2):
    countries = Countries.query.all()
    # print(alpha2)
    countries_descriptions = [present_country(country) for country in countries if present_country(country)["alpha2"] == alpha2]
    return jsonify(countries_descriptions[0])

@app.route("/api/auth/register", methods=["POST"])
def post_register_user():
    user_data = request.get_json()
    #print(user_data)
    users = User.query.all()
    countries = Countries.query.all()
    # print(alpha2)
    users_usernames = [present_user(user)["login"] for user in users]
    codes = [present_country(country)["alpha2"] for country in countries]
    # print(user_data)
    if "login" not in user_data : 
        response = {"reason": "Login required!"}
        response_code = 400
        print((response), response_code)
        return jsonify(response), response_code
    if "email" not in user_data : 
        response = {"reason": "Email required!"}
        response_code = 400
        print((response), response_code)
        return jsonify(response), response_code
    if "countryCode" not in user_data : 
        response = {"reason": "Country code required!"}
        response_code = 400
        print((response), response_code)
        return jsonify(response), response_code
    if "isPublic" not in user_data : 
        response = {"reason": "isPublic required!"}
        response_code = 400
        print((response), response_code)
        return jsonify(response), response_code
    if user_data["countryCode"] not in codes : 
        response = {"reason": "Invalid country code"}
        response_code = 400
        print((response), response_code)
        return jsonify(response), response_code
    if len(user_data["login"]) > 30 : 
        response = {"reason": "Login length exceeded the limit"}
        response_code = 400
        print((response), response_code)
        return jsonify(response), response_code
    if len(user_data["email"]) > 50 : 
        response = {"reason": "Email length exceeded the limit"}
        response_code = 400
        print((response), response_code)
        return jsonify(response), response_code
    
    existing_user = User.query.filter(
        (User.login == user_data["login"]) |
        (User.email == user_data["email"]) |
        (User.phone == user_data.get("phone"))
    ).first()

    if existing_user:
        return jsonify({"reason": "User with this login, email, or phone already exists"}), 409
    
    response = {"profile": {"login": user_data["login"], "email": user_data["email"], "countryCode": user_data["countryCode"], "isPublic": user_data["isPublic"], "phone": user_data["phone"]}}
    response_code = 201

    new_user = User(
        login = user_data["login"],
        email = user_data["email"],
        password = generate_password_hash(user_data["password"]),
        countryCode = user_data["countryCode"],
        isPublic = user_data["isPublic"],
        phone = user_data.get("phone"),
        image = user_data.get("image")
    )
    db.session.add(new_user)
    db.session.commit()

    print((response), response_code)
    return jsonify(response), response_code

@app.route('/api/auth/sign-in', methods=['POST'])
def sign_in():
    data = request.json
    login = data.get('login')
    password = data.get('password')

    if not login or not password:
        return jsonify({"reason": "Login and password are required"}), 400

    user = User.query.filter_by(login=login).first()

    print(user.password, generate_password_hash(password))
    if user and user.password == generate_password_hash(password):
        access_token = create_access_token(identity=str(user.login), expires_delta=datetime.timedelta(hours=1))
        return jsonify(token=access_token), 200
    else:
        return jsonify({"reason": "Invalid login or password"}), 401
    
@app.route('/api/me/profile', methods=['GET', 'PATCH'])
@jwt_required()
def profile():
    if request.method == "GET":
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        if user:
            return jsonify({
                "login": user.login,
                "email": user.email,
                "countryCode": user.countryCode,
                "isPublic": user.isPublic,
                "phone": user.phone,
                "image": user.image
            }), 200
        else:
            return jsonify({"reason": "User not found"}), 401
    elif request.method == "PATCH":
        try:
            data = request.json.pop('password')
        except:
            data = request.json
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        if user:
            if 'login' in data:
                if not isinstance(data['login'], str) or len(data['login']) < 3 or len(data['login']) > 80:
                    return jsonify({"reason": "Login must be a string with a length between 3 and 80 characters"}), 400
                user.login = data['login']
            if 'email' in data:
                if not isinstance(data['email'], str) or len(data['email']) < 5 or len(data['email']) > 120:
                    return jsonify({"reason": "Email must be a string with a length between 5 and 120 characters"}), 400
                existing_user = User.query.filter_by(email=data['email']).first()
                if existing_user and existing_user.id != user_id:
                    return jsonify({"reason": "Email already in use"}), 400
                user.email = data['email']
            if 'countryCode' in data:
                country = Countries.query.filter_by(alpha2=data['countryCode']).first()
                if not country:
                    return jsonify({"reason": "Country with the specified code not found"}), 400
                user.countryCode = data['countryCode']
            if 'isPublic' in data:
                if not isinstance(data['isPublic'], bool):
                    return jsonify({"reason": "IsPublic must be a boolean"}), 400
                user.isPublic = data['isPublic']
            if 'phone' in data:
                if not isinstance(data['phone'], str) or len(data['phone']) < 5 or len(data['phone']) > 15:
                    return jsonify({"reason": "Phone must be a string with a length between 5 and 15 characters"}), 400
                existing_user = User.query.filter_by(phone=data['phone']).first()
                if existing_user and existing_user.id != user_id:
                    return jsonify({"reason": "Phone already in use"}), 400
                user.phone = data['phone']
            if 'image' in data:
                if not isinstance(data['image'], str) or len(data['image']) > 255:
                    return jsonify({"reason": "Image link must be a string with a length not exceeding 255 characters"}), 400
                user.image = data['image']
            db.session.commit()
            return jsonify({
                "login": user.login,
                "email": user.email,
                "countryCode": user.countryCode,
                "isPublic": user.isPublic,
                "phone": user.phone,
                "image": user.image
            }), 200
                            
        

@app.route("/api/me/updatePassword", methods=["POST"])
@jwt_required()
def update_password():
    data = request.json
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if user:
        if user.password == generate_password_hash(data["oldPassword"]):
            if len(data["newPassword"]) < 8 :
                return jsonify({"reason": "Password must be at least 8 characters long"}), 400
            else:
                user.password = generate_password_hash(data["newPassword"])
                db.session.commit()
                return jsonify({"status": "ok"}), 200
        else:
            return jsonify({"reason": "Old password is incorrect"}), 403
        
@app.route('/api/profiles/<profile_login>', methods=['GET', 'POST'])
@jwt_required()
def get_public_profile(profile_login):
    user = User.query.filter_by(login=profile_login, isPublic=1).first()
    if user:
        return jsonify({
                "login": user.login,
                "email": user.email,
                "countryCode": user.countryCode,
                "isPublic": user.isPublic,
                "phone": user.phone,
                "image": user.image
        }), 200
    else:
        return jsonify({"reason": "User not found"}), 403
    
@app.route('/api/profiles/', methods=['GET'])
@jwt_required()
def no_login():
    return jsonify({"reason": "You must be logged in to access this endpoint"}), 403


if __name__ == "__main__":
    # запускаем сервер
    app.run(debug=True, port=57424)