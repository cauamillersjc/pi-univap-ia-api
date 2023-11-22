from flask import Flask, request
from flask_restful import Resource, Api
from flask_cors import CORS
import cv2
import face_recognition
import base64
import numpy as np
from imageio.v2 import imread
import io
import json

app = Flask(__name__)
api = Api(app)

cors = CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

# Função para ler dados do arquivo JSON
def load_users():
    try:
        with open('users.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# Função para gravar dados no arquivo JSON
def save_users(users_data):
    with open('users.json', 'w') as file:
        json.dump(users_data, file)

users = load_users()  # Carrega os dados do arquivo JSON

class Register(Resource):
    def post(self):
        data = request.get_json()
        user = str(data.get('user'))
        password = str(data.get('password'))
        base64_photo = str(data.get('photo'))

        base64_photo = base64_photo.replace("data:image/jpeg;base64,", "")

        try:
            image = imread(io.BytesIO(base64.b64decode(base64_photo)))
            if image is None:
                return {'error': 'Falha ao decodificar a imagem.'}
        except Exception as e:
            return {'error': f'Erro durante a decodificação da imagem: {str(e)}'}

        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(image_rgb)

        photo_filename = f"{user}_photo.jpg"
        photo_path = f"photos/{photo_filename}"

        cv2.imwrite(photo_path, cv2.cvtColor(image, cv2.COLOR_RGB2BGR))

        if face_locations:
            users[user] = {'user': user, 'photo_path': photo_path, 'password': password}
            save_users(users)  # Salva os dados no arquivo JSON

            return {'message': 'Cadastro efetuado com sucesso!'}
        else:
            return {'message': 'Rosto não foi encontrado na foto. Tente novamente!'}, 400

class FaceLogin(Resource):
    def post(self):
        data = request.get_json()
        base64_photo = str(data.get('photo'))

        base64_photo = base64_photo.replace("data:image/jpeg;base64,", "")

        try:
            image = imread(io.BytesIO(base64.b64decode(base64_photo)))
            if image is None:
                return {'error': 'Falha ao decodificar a imagem.'}
        except Exception as e:
            return {'error': f'Erro durante a decodificação da imagem: {str(e)}'}

        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(image_rgb)

        if face_locations:
            for person_id, registration_info in users.items():
                registration_image = face_recognition.load_image_file(registration_info['photo_path'])
                registration_encodings = face_recognition.face_encodings(registration_image)[0]

                comparison_result = face_recognition.compare_faces([registration_encodings], face_recognition.face_encodings(image_rgb)[0])

                if comparison_result[0]:
                    return {'message': 'Autenticação efetuada com sucesso!', 'user': registration_info["user"]}

            return {'error': 'Nenhuma inscrição encontrada para a pessoa na foto.'}
        else:
            return {'error': 'Nenhum rosto encontrado na foto.'}
        
class PasswordLogin(Resource):
    def post(self):
        data = request.get_json()
        user = str(data.get('user'))
        password = str(data.get('password'))

        if user in users:
            if users[user]['password'] == password:
                return {'message': 'Autenticação efetuada com sucesso!', 'user': users[user]['user']}
            else:
                return {'error': 'Senha incorreta.'}
        else:
            return {'error': 'Usuário não encontrado.'}

api.add_resource(Register, '/register')
api.add_resource(FaceLogin, '/login/face')
api.add_resource(PasswordLogin, '/login/password')

if __name__ == '__main__':
    app.run(debug=True)
