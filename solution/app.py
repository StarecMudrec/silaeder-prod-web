from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///countries.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Countries(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)

# создаем базу данных, если ее пока нет
# with app.app_context():
#     db.create_all()

# презенторы - функции, которые представляют модели в виде словарей
def present_artist(artist):
    return {
        'id': artist.id,
        'name': artist.name,
        'description': artist.description
    }

# ендпоинты - реагируют на запросы пользователей


@app.route('/api/ping', methods=['GET'])
def send():
    return jsonify({"status": "ok"}), 200

# получение списка исполнителей
@app.route('/api/artists', methods=['GET'])
def get_all_artists():
    # забираем всех исполнителей из базы
    artists = Artist.query.all()
    # превращаем их в список словарей
    artist_descriptions = [present_artist(artist) for artist in artists]
    # возвращаем ответ в виде списка словарей и типом application/json
    return jsonify(artist_descriptions)

# получение исполнителя по id
@app.route('/api/artists/<int:id>', methods=['GET'])
def get_artist_by_id(id):
    # ищем в базе запись с указанным id - вернется объект типа Artist или None
    artist = Artist.query.filter_by(id=id).first()

    # если исполнитель не найден - сообщаем об этом пользователю
    if not artist:
        return jsonify({'reason': 'Artist not found'}), 404

    # если исполнитель найден - отправляем словарь с его описанием
    return jsonify(present_artist(artist))

# добавление исполнителя
@app.route('/api/artists', methods=['POST'])
def add_artist():
    data = request.get_json()

    name = data.get('name')
    # получаем описание
    description = data.get('description')

    # описание не проверяем - оно может быть и пустым
    if not name:
        return jsonify({'reason': 'Missing name'}), 400
    if Artist.query.filter_by(name=name).first():
        return jsonify({'reason': 'Artist already exists'}), 400

    # добавляем описание к новому исполнителю
    artist = Artist(name=name, description=description)
    db.session.add(artist)
    db.session.commit()

    return jsonify(present_artist(artist))

# PATCH - изменение выбранных свойств исполнителя, в нашем случае - имени
@app.route('/api/artists/<int:id>', methods=['PATCH'])
def update_artist(id):
    data = request.get_json()

    artist = Artist.query.filter_by(id=id).first()
    if not artist:
        return jsonify({'reason': 'Artist not found'}), 404

    # логика PATCH подразумевает, что можно передавть не все свойства, а только те, что нужно поменять.
    # для изменения объекта целиком используется метод PUT
    # если передали имя - проводим проверки для имени
    if 'name' in data:
        name = data.get('name')

        if not name:
            return jsonify({'reason': 'Missing name'}), 400

        if name != artist.name and Artist.query.filter_by(name=name).first():
            return jsonify({'reason': 'Artist already exists'}), 400

        artist.name = name

    # если передали любое описание - меняем описание
    if 'description' in data:
        description = data.get('description')
        artist.description = description

    db.session.commit()

    # возвращаем описание артиста с изменениями
    return jsonify(present_artist(artist))

# запрос типа DELETE - удаление артиста из базы
@app.route('/api/artists/<int:id>', methods=['DELETE'])
def delete_artist(id):
    # находим артиста в базе и возвращаем ошибку, если его нет
    artist = Artist.query.filter_by(id=id).first()

    if not artist:
        return jsonify({'reason': 'Artist not found'}), 404
    # удаляем запись
    db.session.delete(artist)
    # сохраняем изменения
    db.session.commit()

    # возвращаем успешный ответ
    return jsonify({'success': True})

if __name__ == '__main__':
    # запускаем сервер
    app.run(debug=True)