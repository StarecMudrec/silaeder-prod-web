from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///countries.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

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
    phone = db.Column(db.String(), nullable=False)
    image = db.Column(db.Text, nullable=False)

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
    response = {"profile": {"login": user_data["login"], "email": user_data["email"], "countryCode": user_data["countryCode"], "isPublic": user_data["isPublic"], "phone": user_data["phone"]}}
    response_code = 201
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
    if user_data["login"] in users_usernames : 
        response = {"reason": "Username already exists"}
        response_code = 400
        print((response), response_code)
        return jsonify(response), response_code
    print((response), response_code)
    return jsonify(response), response_code


if __name__ == "__main__":
    # запускаем сервер
    app.run(debug=True, port=57424)