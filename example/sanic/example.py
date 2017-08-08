"""
Simple Sanic Restful API
"""
from eventify.event import Event
from eventify.service import Service

from sanic import Sanic
from sanic.response import json
from sanic.views import HTTPMethodView
from sanic_mysql import SanicMysql


# Setup Sanic
app = Sanic(__name__)
app.config.update(
    dict(
        MYSQL=dict(
            host='localhost',
            port=3306,
            user='user',
            password='password',
            db='database'
        )
    )
)
SanicMysql(app)


def set_session(session):
    """
    Setup session
    """
    app.session = session
app.set_session = set_session


@app.listener('before_server_start')
async def before_server_start(app):
    """
    This handles setting up the websocket
    connection to crossbar
    """
    session = Service(handlers=[app])
    app.session = await session.start(start_loop=False)


class SimpleScheduleView(HTTPMethodView):
    """
    Setup HTTP Handler
    """

    async def get(self, request):
        """
        Get schedules with simple query
        """
        results = await request.app.mysql.query('select * from schedule_job limit 3')
        event = Event({
            "name": "QueriedDB",
            "message": results
            })
        await app.session.emit_event(event)
        return json(results)


# Setup routes
app.add_route(SimpleScheduleView.as_view(), '/testschedules')


if __name__ == '__main__':
    app.run()
