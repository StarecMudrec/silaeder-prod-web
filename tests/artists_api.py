import requests

API_URL = 'http://127.0.0.1:5000/api/'

def create_artist_request(name, description=None):
    data = {'name': name}
    if description:
        data['description'] = description
    return requests.post(
        API_URL + 'artists',
        json=data
    )

def get_artist_request(artist_id):
    return requests.get(API_URL + 'artists/' + str(artist_id))

def get_all_artists_request():
    return requests.get(API_URL + 'artists')

def delete_artist_request(artist_id):
    return requests.delete(API_URL + 'artists/' + str(artist_id))

def update_artist_request(artist_id, name=None, description=None):
    data = {}

    if name:
        data['name'] = name
    if description:
        data['description'] = description

    return requests.patch(
        API_URL + 'artists/' + str(artist_id),
        json=data
    )

def run_artists_api_tests():
    # проверяем создание артистов
    artist_response1 = create_artist_request('Test Artist1', 'Description1')
    artist_response2 = create_artist_request('Test Artist2', 'Description2')
    assert artist_response1.status_code == 200
    assert artist_response2.status_code == 200
    print("Artist creation tests passed!")

    # сохраняем id новых артистов
    artist_id1 = artist_response1.json().get('id')
    artist_id2 = artist_response2.json().get('id')

    # проверяем, что нельзя создать артиста с уже использованным именем
    artist_response = create_artist_request('Test Artist1')
    assert artist_response.status_code == 400
    print("Artist name uniqueness tests passed!")

    # проверяем, что можно получить артиста по id
    artist_response = get_artist_request(artist_id1)
    assert artist_response.status_code == 200
    assert artist_response.json().get('name') == 'Test Artist1'
    assert artist_response.json().get('description') == 'Description1'
    print("Get artist by id tests passed!")

    # проверяем, что можно изменить артиста
    artist_response = update_artist_request(artist_id1, 'Test Artist1', 'Updated Description1')
    assert artist_response.status_code == 200
    print("Update artist tests passed!")

    # проверяем, что нельзя задать артисту уже использованное имя при обновлении
    artist_response = update_artist_request(artist_id1, 'Test Artist2')
    assert artist_response.status_code == 400
    print("Update artist name uniqueness tests passed!")

    # проверяем, что можно изменить артиста
    artist_response = update_artist_request(artist_id1, 'Test Artist3', 'Another Description')
    assert artist_response.status_code == 200
    print("Update artist tests passed!")

    # проверяем, что можно получить список артистов
    artist_response = get_all_artists_request()
    assert artist_response.status_code == 200
    assert len(artist_response.json()) == 2
    print("Get all artists tests passed!")

    # проверяем, что можно удалить артиста
    artist_response = delete_artist_request(artist_id1)
    assert artist_response.status_code == 200
    print("Delete artist tests passed!")

    artist_response = get_artist_request(artist_id1)
    assert artist_response.status_code == 404
    print("Delete artist confirmation tests passed!")

    # удаляем второго артиста из базы
    artist_response = delete_artist_request(artist_id2)
    assert artist_response.status_code == 200
    print("All tests passed!")

if __name__ == '__main__':
    run_artists_api_tests()