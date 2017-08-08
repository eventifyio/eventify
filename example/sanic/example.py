"""
Simple Sanic Restful API
"""
import os

from eventify.event import Event
from eventify.service import Service

from sanic import Sanic
from sanic.response import json, text
from sanic.views import HTTPMethodView
from sanic_mysql import SanicMysql


app = Sanic(__name__)
app.config.update(dict(MYSQL=dict(host='betterclouds-dev.cc8axsfy55ku.us-east-1.rds.amazonaws.com', port=3306,
                       user='cliff', password='uTbrEveLD5Ef4Juh',
                       db='schedule_service')))

SanicMysql(app)


def set_session(session):
    print('called')
    print(session)
    app.session = session

app.set_session = set_session
@app.listener('before_server_start')
async def before_server_start(app, loop):
    print('connecting to crossbar')
    session = Service(handlers=[app])
    app.session = await session.start(start_loop=False)

class SimpleScheduleView(HTTPMethodView):

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


app.add_route(SimpleScheduleView.as_view(), '/testschedules')

if __name__ == '__main__':
    app.run()

