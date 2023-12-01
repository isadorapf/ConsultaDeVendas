from flask import Flask, render_template, request, redirect, url_for, session, Response
import pyodbc

app = Flask(__name__)
app.secret_key = 'supersecretkey'

server = 'DESKTOP-T7G8FU4\SOFTWAREIMPACTA'
database = 'SFTIMPACTA'


@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username_form = request.form.get('username')
        password_form = request.form.get('password')
        conn_str = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username_form};PWD={password_form}'
        try:
            conn = pyodbc.connect(conn_str)
            conn.close()
            session['authenticated'] = True
            session['username'] = username_form
            session['password'] = password_form
            return redirect(url_for('index'))
        except Exception as e:
            print("Database connection failed:", e)
            session['authenticated'] = False
            return render_template('login.html', message='Credenciais inválidas')
    return render_template('login.html')


@app.route('/index')
def index():
    if 'authenticated' in session and session['authenticated']:
        return render_template('TelaPrincipal.html')
    else:
        return redirect(url_for('login'))


def fetch_table_data(table_name, filters=None, as_list=False):
    conn_str = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={session.get("username")};PWD={session.get("password")}'
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        query = f"SELECT * FROM {table_name}"
        params = []

        if filters:
            where_clauses = []
            for key, value in filters.items():
                if value:  # consider only non-empty filters
                    where_clauses.append(f"{key} LIKE ?")
                    params.append(f"%{value}%")

            if where_clauses:
                query += " WHERE " + " AND ".join(where_clauses)

        cursor.execute(query, params)
        columns = [column[0] for column in cursor.description]
        rows = cursor.fetchall()
        conn.close()

        if as_list:
            return {"columns": columns, "rows": rows}
        else:
            table_data = "<table border='1'>"
            table_data += "<thead><tr>" + "".join([f"<th>{col}</th>" for col in columns]) + "</tr></thead>"
            table_data += "<tbody>" + "".join(
                [f"<tr>{''.join([f'<td>{cell}</td>' for cell in row])}</tr>" for row in rows]) + "</tbody>"
            table_data += "</table>"
            return table_data

    except Exception as e:
        print("Error:", e)
        return "Erro ao buscar dados", 500


@app.route('/get_table_data/<table_name>', methods=['GET', 'POST'])
def get_table_data(table_name):
    if table_name not in ['fornecedores', 'clientes', 'vendas', 'produtos']:
        return "Tabela não reconhecida", 400

    if 'authenticated' not in session or not session['authenticated']:
        return "Não autenticado", 401

    # Se for POST, obtem os filtros do corpo da requisição
    filters = request.json if request.method == 'POST' else None
    return fetch_table_data(table_name, filters)


@app.route('/export_csv/<table_name>', methods=['POST'])
def export_csv(table_name):
    if 'authenticated' not in session or not session['authenticated']:
        return "Não autenticado", 401

    filters = request.json
    data = fetch_table_data(table_name, filters, as_list=True)

    def generate():
        yield table_name + '\n'
        yield ','.join(data['columns']) + '\n'
        for row in data['rows']:
            yield ','.join([str(cell) for cell in row]) + '\n'

    return Response(generate(), mimetype='text/csv',
                    headers={"Content-Disposition": f"attachment;filename={table_name}.csv"})


if __name__ == '__main__':
    app.run(debug=True)
