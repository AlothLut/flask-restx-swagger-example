from flask import Flask
from flask_restx import Api, Resource, fields, reqparse
import statistics
from operator import itemgetter

app = Flask(__name__)
api = Api(app, version='1.0', title='Literary Works API', description='Manage Literary Works Dataset')

# объявляем модель литературные работы
literary_work = api.model('LiteraryWork', {
    'id': fields.Integer(required=True, description='The work identifier'),
    'title': fields.String(required=True, description='The title of the literary work'),
    'author': fields.String(required=True, description='The author of the literary work'),
    'year_published': fields.Integer(required=True, description='The year the literary work was published'),
    'rating': fields.Float(required=True, description='The rating of the literary work')
})

# лист для имитации хранения данных вместо бд
literary_works = []

# парсер для метода с сортировкой
sort_parser = reqparse.RequestParser()
for field in ['id', 'title', 'author', 'year_published', 'rating']:
    sort_parser.add_argument(field, type=str, help=f"Sorting by {field} asc o desc", location='args')


# CRUD operations
@api.route('/literary-works')
class LiteraryWorkList(Resource):
    @api.marshal_list_with(literary_work)
    @api.expect(sort_parser)
    def get(self):
        """Получаем все работы с сортировкой или без"""
        args = sort_parser.parse_args()
        sorted_literary_works = literary_works
        if any(args[field_name] is not None for field_name in ['id', 'title', 'author', 'year_published', 'rating']):
            # Itemgetter можно использовать вместо лямбда-функции для достижения аналогичной функциональности.
            # Выводит то же самое, что и sorted() и лямбда, но имеет другую внутреннюю реализацию.
            # Он берет ключи словарей и преобразует их в кортежи.
            for field_name in ['id', 'title', 'author', 'year_published', 'rating']:
                if args[field_name] is None:
                    continue
                if args[field_name] == "asc":
                    reverse = True
                else:
                    reverse = False
                sorted_literary_works = sorted(literary_works, key=itemgetter(field_name), reverse=reverse)
        return sorted_literary_works

    @api.expect(literary_work)
    @api.marshal_with(literary_work, code=201)
    def post(self):
        """Добавялев новое произведение"""
        new_work = api.payload
        literary_works.append(new_work)
        return new_work, 201


@api.route('/literary-works/<int:id>')
class LiteraryWork(Resource):
    @api.marshal_with(literary_work)
    def get(self, id):
        """Получаем литературное произведение по id"""
        for work in literary_works:
            if work['id'] == id:
                return work
        api.abort(404, f"Literary Work {id} not found")

    @api.expect(literary_work)
    @api.marshal_with(literary_work)
    def put(self, id):
        """Обновляем литературное произведение по id"""
        for work in literary_works:
            if work['id'] == id:
                work.update(api.payload)
                return work
        api.abort(404, f"Literary Work {id} not found")

    def delete(self, id):
        """Удаляем литературное произведение по id"""
        for index, work in enumerate(literary_works):
            if work['id'] == id:
                del literary_works[index]
                return '', 204
        api.abort(404, f"Literary Work {id} not found")


@api.route('/literary-works/aggregates')
class LiteraryWorkAggregates(Resource):
    def get(self):
        """Получаем среднее, максимальное и минимальное значение по числовым полям"""
        ratings = [work['rating'] for work in literary_works]
        year_published = [work['year_published'] for work in literary_works]
        return {
            'average_rating': statistics.mean(ratings) if ratings else 0,
            'max_rating': max(ratings) if ratings else 0,
            'min_rating': min(ratings) if ratings else 0,
            'average_year_published': statistics.mean(year_published) if year_published else 0,
            'max_year_published': max(year_published) if year_published else 0,
            'min_year_published': min(year_published) if year_published else 0
        }


if __name__ == '__main__':
    app.run(debug=True)
