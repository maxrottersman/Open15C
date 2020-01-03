import psycopg2
import sshtunnel

sshtunnel.SSH_TIMEOUT = 5.0
sshtunnel.TUNNEL_TIMEOUT = 5.0

with sshtunnel.SSHTunnelForwarder(
    ('ssh.pythonanywhere.com'),
    ssh_username='maxrottersman', \
    ssh_password='3hZ!Tq-vQY39_-4', \
    remote_bind_address=('maxrottersman-1439.postgres.pythonanywhere-services.com', 11439)
) as tunnel:
    connection = psycopg2.connect(
        user='super', password='pa314271',
        host='127.0.0.1', port=tunnel.local_bind_port,
        database='SECFunds',
    )
    # Do stuff
    connection.close()