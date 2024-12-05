import numpy as np
import matplotlib.pyplot as plt

# Du lieu cho do thi thu nhat
x1 = np.linspace(-3 * np.pi, 0, 500)  # x trong khoang [-3pi, 0]
y1 = 1.5 * np.sin(x1)  # Ham y = 1.5sin(x)

# Du lieu cho do thi thu hai (do thi cuc trong toa do Descartes)
theta = np.linspace(0, 2 * np.pi, 500)  # Goc theta tu 0 den 2pi
r = 2 + np.cos(10 * theta) + 2 * np.sin(5 * theta)  # Ham r
x_polar = r * np.cos(theta)  # Chuyen sang x
y_polar = r * np.sin(theta)  # Chuyen sang y

# Du lieu cho do thi thu ba
x2 = np.linspace(0, 3 * np.pi, 500)  # x trong khoang [0, 3pi]
y2 = 1.5 * np.sin(x2)  # Ham y = 1.5sin(x)

# Ve do thi
plt.figure(figsize=(10, 6))

# Do thi thu nhat
plt.plot(x1, y1, 'r--', label='y = 1.5sin(x) with x in [-3pi, 0]')  # Duong gach do (--)

# Do thi thu hai (do thi cuc)
plt.plot(x_polar, y_polar, 'g-', label='r = 2 + cos(10*theta) + 2sin(5*theta)')  # Duong lien xanh la (-)

# Do thi thu ba
plt.plot(x2, y2, 'b:', label='y = 1.5sin(x) with x in [0, 3pi]')  # Duong cham xanh duong (:)

# Thiet lap ty le deu nhau tren truc x, y
plt.axis('equal')

# Hien thi luoi, chu thich, va nhan
plt.grid(True)  # Bat luoi
plt.legend()  # Hien thi chu thich
plt.xlabel('x')  # Nhan truc x
plt.ylabel('y')  # Nhan truc y

# Hien thi do thi
plt.show()
