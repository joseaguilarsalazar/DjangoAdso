import matplotlib.pyplot as plt
import numpy as np

# --- Data ---

years = np.arange(1995, 2026)

# Approximate annual inflation rates (%) for Peru
inflation = {
    1995: 11.13, 1996: 11.54, 1997: 8.56, 1998: 7.25, 1999: 3.47,
    2000: 3.76, 2001: 1.98, 2002: 0.19, 2003: 2.26, 2004: 3.66,
    2005: 1.62, 2006: 2.0, 2007: 1.78, 2008: 5.79, 2009: 2.94,
    2010: 1.53, 2011: 3.37, 2012: 3.61, 2013: 2.77, 2014: 3.41,
    2015: 3.4, 2016: 3.56, 2017: 2.99, 2018: 1.51, 2019: 2.25,
    2020: 2.0, 2021: 4.27, 2022: 8.33, 2023: 6.46, 2024: 2.01, 2025: 1.7
}

# Real historical minimum wage (Soles)
# Source: Ministerio de Trabajo / historical references
real_min_wage = {
    1995: 132, 2000: 410, 2003: 460, 2006: 500, 2008: 550,
    2011: 580, 2012: 675, 2016: 850, 2018: 930, 2022: 1025, 2025: 1130
}

# --- Compute inflation-adjusted wage ---
base_wage = 132  # 1995 minimum wage in soles
adjusted_wage = [base_wage]
for i in range(1, len(years)):
    prev = adjusted_wage[-1]
    rate = inflation.get(years[i], 0)
    adjusted_wage.append(prev * (1 + rate / 100))

# --- Fill real wage series ---
real_series = []
last = base_wage
for y in years:
    if y in real_min_wage:
        last = real_min_wage[y]
    real_series.append(last)

# --- Plot ---
plt.figure(figsize=(10,6))
plt.plot(years, adjusted_wage, label="Salario mínimo ajustado por inflación (manteniendo poder adquisitivo)", color="tab:blue")
plt.plot(years, real_series, label="Salario mínimo real establecido", color="tab:red", linestyle="--")

plt.title("Evolución del salario mínimo vs inflación en Perú (1995–2025)")
plt.xlabel("Año")
plt.ylabel("Salario mensual (S/)")
plt.grid(True, linestyle=":")
plt.legend()
plt.tight_layout()
plt.show()
