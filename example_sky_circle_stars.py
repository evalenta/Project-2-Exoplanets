"""
Example: Plot stars on a circular sky chart based on location and time.

Run: python example_sky_circle_stars.py

Uses Skyfield for star positions. Install with: pip install skyfield
Skyfield will download star catalogs automatically on first run.
"""

import numpy as np
import matplotlib.pyplot as plt
from skyfield.api import load, Star
from skyfield.data import hipparcos

# --- Configuration (change these to match your location) ---
LATITUDE = 40.0   # degrees North (e.g., Columbus OH)
LONGITUDE = -83.0  # degrees West
# Use current time, or set a specific UTC time
USE_CURRENT_TIME = True

# --- Load Skyfield data ---
ts = load.timescale()
eph = load("de421.bsp")  # Planetary ephemeris (downloads on first run)

# Load Hipparcos star catalog
with load.open(hipparcos.URL) as f:
    stars = hipparcos.load_dataframe(f)

# Keep only brighter stars (magnitude < 5) to keep the plot readable
bright_stars = stars[stars["magnitude"] < 5.0]

# --- Set location and time ---
observer = eph["earth"] + ts.from_latlon(LATITUDE, LONGITUDE)

if USE_CURRENT_TIME:
    t = ts.now()
else:
    # Example: 2025-03-13 02:00 UTC (evening in Ohio)
    t = ts.utc(2025, 3, 13, 2, 0, 0)

# --- Compute alt/az for each star ---
star_objects = [Star.from_dataframe(row) for _, row in bright_stars.iterrows()]
star_positions = eph["earth"].at(t).observe(star_objects)

# Get altitude (degrees) and azimuth (degrees)
alt, az, _ = star_positions.apparent().altaz()

# --- Filter: only stars above horizon ---
above_horizon = alt.degrees > 0
alt_deg = alt.degrees[above_horizon]
az_deg = az.degrees[above_horizon]
mag = bright_stars["magnitude"].values[above_horizon]

# --- Project onto circle: r = 1 - (altitude/90), center=zenith, edge=horizon ---
# Azimuth: 0 = North, 90 = East. For a circle with North up:
# x = r * sin(azimuth), y = r * cos(azimuth)
r = 1 - (alt_deg / 90.0)
az_rad = np.deg2rad(az_deg)
x = r * np.sin(az_rad)
y = r * np.cos(az_rad)

# Star size: brighter stars = bigger dots (magnitude is inverted: lower = brighter)
sizes = 100 * (6 - mag)
sizes = np.clip(sizes, 5, 80)

# --- Plot ---
fig, ax = plt.subplots(figsize=(8, 8), facecolor="black")
ax.set_facecolor("black")

# Outer circle (horizon)
circle = plt.Circle((0, 0), 1, edgecolor="white", facecolor="darkblue", linewidth=1)
ax.add_artist(circle)

# Grid
for r_val in [0.25, 0.5, 0.75]:
    ring = plt.Circle((0, 0), r_val, edgecolor="gray", facecolor="none", linewidth=0.5)
    ax.add_artist(ring)
for angle_deg in range(0, 360, 30):
    angle = np.deg2rad(angle_deg)
    xi, yi = np.cos(angle), np.sin(angle)
    ax.plot([0, xi], [0, yi], color="gray", linewidth=0.5)

# Stars
ax.scatter(x, y, s=sizes, c="white", alpha=0.9, edgecolors="none")

# NSEW labels
ax.text(0.5, 1.02, "N", transform=ax.transAxes, ha="center", va="bottom", fontsize=14, color="white")
ax.text(0.5, -0.02, "S", transform=ax.transAxes, ha="center", va="top", fontsize=14, color="white")
ax.text(1.02, 0.5, "E", transform=ax.transAxes, ha="left", va="center", fontsize=14, color="white")
ax.text(-0.02, 0.5, "W", transform=ax.transAxes, ha="right", va="center", fontsize=14, color="white")

ax.set_aspect("equal")
ax.set_xlim(-1.2, 1.2)
ax.set_ylim(-1.2, 1.2)
ax.axis("off")
ax.set_title(f"Sky at lat={LATITUDE}°N, lon={LONGITUDE}°\n{t.utc_strftime('%Y-%m-%d %H:%M')} UTC", color="white")

plt.tight_layout()
plt.show()
