from flask import Flask, request, render_template
from ranking import SearchRank

app = Flask(__name__)

rank = SearchRank('articles_collection')
# rank = SearchRank('small_coll')


@app.route('/')
def index():
    if request.args:
        search_query = request.args['query']
        res = rank.query(search_query)
        return render_template('index.html', result=res)
    return render_template('index.html', result=[])


if __name__ == '__main__':
    app.run()
