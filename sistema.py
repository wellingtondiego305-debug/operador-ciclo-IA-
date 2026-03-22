import pandas as pd

df = pd.read_csv("historico.csv")

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

    # OVER
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

    # UNDER
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


# ===== BACKTEST =====

saldo = 0
stake = 1
odd = 2.0

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
        saldo += stake * (odd - 1)
    else:
        saldo -= stake

    print(f"Jogo {i} → {zona} | Gols: {gols} | {'WIN' if win else 'LOSS'}")

print("\nResultado final:", saldo)
