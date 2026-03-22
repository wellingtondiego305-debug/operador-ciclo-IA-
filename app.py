from flask import Flask, render_template_string
import pandas as pd

app = Flask(__name__)

def detectar_zona(df, i):
    if i < 20:
        return "NEUTRO", 0

    ultimos20 = df["TotalGols"].iloc[i-20:i]
    ultimos10 = df["TotalGols"].iloc[i-10:i]

    over20 = sum(1 for x in ultimos20 if x >= 3)
    media10 = sum(ultimos10) / len(ultimos10)

    ultimos5 = df["TotalGols"].iloc[i-5:i]

    score_over = 0
    score_under = 0

    if over20 <= 7:
        score_over += 2
    if all(x < 3 for x in ultimos5[-3:]):
        score_over += 2
    if media10 < 2.3:
        score_over += 2

    atraso = 0
    for j in range(i-1, -1, -1):
        if df.loc[j, "TotalGols"] >= 3:
            break
        atraso += 1

    if atraso >= 4:
        score_over += 2

    if over20 >= 11:
        score_under += 2
    if all(x >= 3 for x in ultimos5[-2:]):
        score_under += 2
    if media10 > 2.8:
        score_under += 2
    if atraso <= 1:
        score_under += 2

    if score_over >= 5:
        return "OVER", score_over
    elif score_under >= 5:
        return "UNDER", score_under
    else:
        return "NEUTRO", max(score_over, score_under)


@app.route("/")
def home():
    df = pd.read_csv("historico.csv")

    resultados = []
    saldo = 0

    for i in range(len(df)):
        zona, score = detectar_zona(df, i)

        if zona == "NEUTRO":
            continue

        gols = df.loc[i, "TotalGols"]

        if zona == "OVER":
            win = gols >= 3
        else:
            win = gols <= 2

        if win:
            saldo += 1
        else:
            saldo -= 1

        resultados.append(f"Jogo {i} → {zona} (score {score}) | Gols: {gols} | {'WIN' if win else 'LOSS'}")

    html = """
    <h1>📊 Operador IA - Futebol Virtual</h1>
    <h2>Saldo: {{saldo}}</h2>
    <a href="/">🔄 Rodar novamente</a>
    <hr>
    {% for r in resultados %}
        <p>{{r}}</p>
    {% endfor %}
    """

    return render_template_string(html, resultados=resultados, saldo=saldo)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
