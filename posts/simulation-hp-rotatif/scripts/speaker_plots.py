#| output: false

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.gridspec as gridspec
import matplotlib.colors as mcolors
from scipy import signal # For filter frequency responses
import os # For creating directories

# --- Parameters (Global, used by both figures) ---
R_SHAFT = 0.1          # r, shaft length (meters)
S_SPEAKER_INCH = 4.0   # <<< Speaker diameter in INCHES >>>
P_COORD = (10*R_SHAFT, 0)       # <<< LISTENER POSITION (x, y) meters >>>

N_FRAMES_ANIM = 120
N_POINTS_EVOLUTION = 300
C_SOUND = 340.0
FREQ_MIN, FREQ_MAX = 20, 20000
N_FREQ_POINTS = 500
EPSILON = 1e-12
FS_SAMPLE_RATE = 48000.0 # Sample rate for Faust digital filter calculations

# --- Faust-specific Parameters ---
FAUST_HS_GAIN_LIN = 0.2 # Fixed linear gain for the high-shelves in Faust code
FAUST_HS_GAIN_DB = 20 * np.log10(FAUST_HS_GAIN_LIN) # for info

# --- Conversion ---
INCH_TO_METER = 0.0254
S_SPEAKER = S_SPEAKER_INCH * INCH_TO_METER

# --- Output Directory for GIFs ---
RESSOURCES_DIR = "./resources"

# --- Helper function for speaker coordinates (S, S1, S2) ---
def get_speaker_coords(theta, r_shaft, s_speaker_m):
    s_half = s_speaker_m / 2.0
    cos_t, sin_t = np.cos(theta), np.sin(theta)
    x_S = r_shaft * cos_t
    y_S = r_shaft * sin_t
    x_S1 = x_S - s_half * sin_t
    y_S1 = y_S + s_half * cos_t
    x_S2 = x_S + s_half * sin_t
    y_S2 = y_S - s_half * cos_t
    return (x_S, y_S), (x_S1, y_S1), (x_S2, y_S2)

# --- General Distance Calculation ---
def calculate_general_distances(theta, r_shaft, s_speaker_m, p_coord):
    if r_shaft <= 0 or s_speaker_m <= 0:
        return ((np.full_like(theta, np.nan),
                 np.full_like(theta, np.nan),
                 np.full_like(theta, np.nan))
                if isinstance(theta, np.ndarray) else (np.nan, np.nan, np.nan))
    theta_arr = np.asarray(theta)
    px, py = p_coord
    (x_S, y_S), (x_S1, y_S1), (x_S2, y_S2) = get_speaker_coords(theta_arr, r_shaft, s_speaker_m)
    ps = np.hypot(x_S - px, y_S - py)
    ps1 = np.hypot(x_S1 - px, y_S1 - py)
    ps2 = np.hypot(x_S2 - px, y_S2 - py)
    if np.isscalar(theta):
        return ps.item(), ps1.item(), ps2.item()
    else:
        return ps, ps1, ps2

# --- Filter Response Functions (Global, used by new figure) ---
freq_axis_global = np.logspace(np.log10(FREQ_MIN), np.log10(FREQ_MAX), N_FREQ_POINTS)

# Original LP filter (not used by Faust model in fig_new but kept for completeness)
def get_lowpass_response(f_c_lp, freqs=freq_axis_global):
    f_c_lp = max(f_c_lp, EPSILON)
    mag_sq = 1.0 / (1.0 + (freqs / f_c_lp)**2)
    return 10 * np.log10(np.maximum(mag_sq, EPSILON**2))

# Original HS filter (not used by Faust model in fig_new but kept for completeness)
def get_highshelf_response(f_c_hs, q_hs, gain_db, freqs=freq_axis_global):
    f_c_hs = max(f_c_hs, EPSILON)
    wc_hs = 2 * np.pi * f_c_hs
    A_shelf = 10**(gain_db / 40.0)
    omegas = 2 * np.pi * freqs

    if abs(A_shelf - 1.0) < EPSILON :
        b = [1.0, 0, wc_hs**2]
        a = [1.0, 0, wc_hs**2]
    elif A_shelf > EPSILON:
        b = [A_shelf**2, A_shelf * wc_hs / q_hs, wc_hs**2]
        a = [1.0, (1.0/A_shelf) * wc_hs / q_hs, wc_hs**2]
    else: # gain_db is very negative
        b = [EPSILON**2, EPSILON * wc_hs / q_hs, wc_hs**2]
        a = [1.0,  1E6 * wc_hs / q_hs, wc_hs**2] 

    _, h_resp = signal.freqs(b, a, worN=omegas)
    return 20 * np.log10(np.maximum(np.abs(h_resp), EPSILON))

def get_comb_filter_response(delay_s, freqs=freq_axis_global):
    delay_s = max(delay_s, 0)
    omega_d = 2 * np.pi * freqs * delay_s
    mag = np.abs(np.cos(omega_d / 2.0)) 
    return 20 * np.log10(np.maximum(mag, EPSILON))

# New function for Faust's highshelf1
def get_faust_highshelf1_response(fc, gain_linear, fs_sample_rate, freqs_hz=freq_axis_global):
    fc = np.clip(fc, FREQ_MIN, FREQ_MAX) 
    gain_linear = np.maximum(gain_linear, EPSILON)

    if fs_sample_rate <= 0 or fc <= 0: 
        return np.zeros_like(freqs_hz)

    K = 2 * np.tan(np.pi * fc / fs_sample_rate)
    
    a_0_denom = 2 + K
    if abs(a_0_denom) < EPSILON: 
        return np.zeros_like(freqs_hz)
    
    b_coeffs = [(2 * gain_linear + K) / a_0_denom, (K - 2 * gain_linear) / a_0_denom]
    a_coeffs = [1, (K - 2) / a_0_denom]

    w, h_resp = signal.freqz(b_coeffs, a_coeffs, worN=freqs_hz, fs=fs_sample_rate)
    return 20 * np.log10(np.maximum(np.abs(h_resp), EPSILON))


# --- START OF ORIGINAL SCRIPT'S PLOTTING ---
fig = plt.figure(figsize=(14, 10))
gs_orig = gridspec.GridSpec(3, 3, figure=fig, hspace=0.45, wspace=0.35)

ax_anim_orig = fig.add_subplot(gs_orig[:2, :2])
ax_time_delay_orig = fig.add_subplot(gs_orig[0, 2])
ax_comb_delay_orig = fig.add_subplot(gs_orig[1, 2])
ax_cutoff_evo_orig = fig.add_subplot(gs_orig[2, 2]) # This was for the old LP fc
ax_gain_evo_orig = fig.add_subplot(gs_orig[2, 0])   # This was for the old HS gain
ax_phase_evo_orig = fig.add_subplot(gs_orig[2, 1])

colors_orig = mcolors.TABLEAU_COLORS

ax_anim_orig.set_title('Rotating Speaker Animation (Original Model)')
ax_anim_orig.set_xlabel('X coordinate (m)')
ax_anim_orig.set_ylabel('Y coordinate (m)')
ax_anim_orig.set_aspect('equal', adjustable='box')
max_radius_orig = max(np.hypot(P_COORD[0], P_COORD[1]), R_SHAFT + S_SPEAKER / 2) if S_SPEAKER > 0 else R_SHAFT
plot_limit_orig = max_radius_orig * 1.3 if max_radius_orig > 0 else 1.0
ax_anim_orig.set_xlim(-plot_limit_orig, plot_limit_orig)
ax_anim_orig.set_ylim(-plot_limit_orig, plot_limit_orig)
circle_C_plot_orig = plt.Circle((0, 0), R_SHAFT, color='dodgerblue', fill=False, ls='--', lw=1.5, label='Path of S')
ax_anim_orig.add_artist(circle_C_plot_orig)
point_P_plot_orig = ax_anim_orig.plot(P_COORD[0], P_COORD[1], 'ko', ms=8, label='P (Listener)')
ax_anim_orig.text(P_COORD[0] * 1.02, P_COORD[1] * 1.02, ' P', fontsize=10, color='black', ha='left', va='bottom')
line_OS_anim_orig, = ax_anim_orig.plot([], [], 'g:', lw=1, label='Shaft OS')
point_S_anim_orig, = ax_anim_orig.plot([], [], 'ro', ms=6, label='S')
text_S_anim_orig = ax_anim_orig.text(0, 0, ' S', fontsize=10, color='red', ha='left', va='bottom')
line_S1S2_anim_orig, = ax_anim_orig.plot([], [], 'crimson', lw=3, label='S1-S2')
point_S1_anim_orig, = ax_anim_orig.plot([], [], marker='o', color='crimson', ms=4)
text_S1_anim_orig = ax_anim_orig.text(0, 0, ' S1', fontsize=10, color='crimson', ha='left', va='bottom')
point_S2_anim_orig, = ax_anim_orig.plot([], [], marker='o', color='crimson', ms=4)
text_S2_anim_orig = ax_anim_orig.text(0, 0, ' S2', fontsize=10, color='crimson', ha='left', va='bottom')
ax_anim_orig.grid(True, linestyle=':', alpha=0.6)

interval_orig_ms = 40
fps_orig = 1000 / interval_orig_ms

def init_animation_orig():
    line_OS_anim_orig.set_data([], [])
    point_S_anim_orig.set_data([], [])
    text_S_anim_orig.set_position((0,0)); text_S_anim_orig.set_text('')
    line_S1S2_anim_orig.set_data([], [])
    point_S1_anim_orig.set_data([], []); text_S1_anim_orig.set_position((0,0)); text_S1_anim_orig.set_text('')
    point_S2_anim_orig.set_data([], []); text_S2_anim_orig.set_position((0,0)); text_S2_anim_orig.set_text('')
    return (line_OS_anim_orig, point_S_anim_orig, text_S_anim_orig,
            line_S1S2_anim_orig, point_S1_anim_orig, text_S1_anim_orig,
            point_S2_anim_orig, text_S2_anim_orig)

def update_animation_orig(frame_num):
    theta = (frame_num / N_FRAMES_ANIM) * 2 * np.pi
    (x_S, y_S), (x_S1, y_S1), (x_S2, y_S2) = get_speaker_coords(theta, R_SHAFT, S_SPEAKER)
    text_offset_x = 0.03 * plot_limit_orig
    text_offset_y = 0.03 * plot_limit_orig
    line_OS_anim_orig.set_data([0, x_S], [0, y_S])
    point_S_anim_orig.set_data([x_S], [y_S])
    text_S_anim_orig.set_position((x_S + text_offset_x, y_S + text_offset_y)); text_S_anim_orig.set_text(' S')
    line_S1S2_anim_orig.set_data([x_S1, x_S2], [y_S1, y_S2])
    point_S1_anim_orig.set_data([x_S1], [y_S1]); text_S1_anim_orig.set_position((x_S1 + text_offset_x, y_S1 + text_offset_y)); text_S1_anim_orig.set_text(' S1')
    point_S2_anim_orig.set_data([x_S2], [y_S2]); text_S2_anim_orig.set_position((x_S2 + text_offset_x, y_S2 + text_offset_y)); text_S2_anim_orig.set_text(' S2')
    return (line_OS_anim_orig, point_S_anim_orig, text_S_anim_orig,
            line_S1S2_anim_orig, point_S1_anim_orig, text_S1_anim_orig,
            point_S2_anim_orig, text_S2_anim_orig)

ani_orig = animation.FuncAnimation(fig, update_animation_orig, frames=N_FRAMES_ANIM,
                              init_func=init_animation_orig, blit=True, interval=interval_orig_ms)

theta_evolution_angles_orig = np.linspace(0, 2 * np.pi, N_POINTS_EVOLUTION)
ps_evo_orig, ps1_evo_orig, ps2_evo_orig = calculate_general_distances(
    theta_evolution_angles_orig, R_SHAFT, S_SPEAKER, P_COORD
)
valid_data_orig = not (np.any(np.isnan(ps_evo_orig)) or np.any(np.isnan(ps1_evo_orig)) or np.any(np.isnan(ps2_evo_orig)))

def setup_evolution_axes_orig(ax, title, ylabel):
    ax.set_title(title, fontsize=11)
    ax.set_xlabel('Speaker Rotation Angle $\Theta$ (rad)')
    ax.set_ylabel(ylabel)
    ax.grid(True, linestyle=':', alpha=0.7)
    ax.set_xticks([0, np.pi/2, np.pi, 3*np.pi/2, 2*np.pi])
    ax.set_xticklabels(['0', '$\pi/2$', '$\pi$', '$3\pi/2$', '$2\pi$'])
    ax.set_xlim(0, 2*np.pi)
    ax.tick_params(axis='both', which='major', labelsize=9)

if valid_data_orig:
    time_delay_ps_orig = ps_evo_orig / C_SOUND * 1000
    time_delay_ps_orig = time_delay_ps_orig - np.min(time_delay_ps_orig)
    ax_time_delay_orig.plot(theta_evolution_angles_orig, time_delay_ps_orig, color=colors_orig['tab:blue'])
    ax_time_delay_orig.set_ylim(bottom=0)
setup_evolution_axes_orig(ax_time_delay_orig, 'Rel. Time Delay from $S$', 'Rel. Delay (ms)')

if valid_data_orig:
    abs_diff_ps1_ps2_orig = np.abs(ps1_evo_orig - ps2_evo_orig)
    comb_delay_time_orig = abs_diff_ps1_ps2_orig / C_SOUND * 1000
    ax_comb_delay_orig.plot(theta_evolution_angles_orig, comb_delay_time_orig, color=colors_orig['tab:cyan'])
    ax_comb_delay_orig.set_ylim(bottom=0)
setup_evolution_axes_orig(ax_comb_delay_orig, 'Comb Delay $|PS_1-PS_2|/c$', 'Delay (ms)')

f_c_lp_orig_model_raw = C_SOUND / (2*S_SPEAKER*np.abs(np.sin(theta_evolution_angles_orig))+EPSILON) if S_SPEAKER > 0 else np.full_like(theta_evolution_angles_orig, FREQ_MAX)
f_c_lp_orig_model = np.minimum(f_c_lp_orig_model_raw, FREQ_MAX)
ax_cutoff_evo_orig.plot(theta_evolution_angles_orig, f_c_lp_orig_model, color=colors_orig['tab:orange'])
ax_cutoff_evo_orig.set_yscale('log')
ax_cutoff_evo_orig.set_ylim(100, FREQ_MAX * 1.2)
if S_SPEAKER > 0 and np.any(np.isfinite(f_c_lp_orig_model)) :
    f_c_min_lp_orig_model = np.min(f_c_lp_orig_model[np.isfinite(f_c_lp_orig_model)])
    ax_cutoff_evo_orig.axhline(f_c_min_lp_orig_model, color='red', linestyle=':', linewidth=1.0, alpha=0.7)
    ax_cutoff_evo_orig.text(0.98, f_c_min_lp_orig_model, f' Min $f_c$: {f_c_min_lp_orig_model:.0f} Hz ',
                       transform=ax_cutoff_evo_orig.get_yaxis_transform(), ha='right', va='bottom', fontsize=9, color='red',
                       bbox=dict(boxstyle='round,pad=0.2', fc='white', ec='none', alpha=0.7))
setup_evolution_axes_orig(ax_cutoff_evo_orig, 'Orig. LP Model: $f_c \propto 1/|sin(\Theta)|$', '$f_c$ (Hz)')

# g_max_orig_hs_model, g_min_orig_hs_model = 0, -12
# g_highshelf_orig_model = g_max_orig_hs_model - (g_max_orig_hs_model - g_min_orig_hs_model) * (0.5 - np.cos(theta_evolution_angles_orig) * 0.5)
f2_highshelf = 20000*np.power((3000/20000), 0.5 - np.cos(theta_evolution_angles_orig) * 0.5)
ax_gain_evo_orig.plot(theta_evolution_angles_orig, f2_highshelf, color=colors_orig['tab:pink'])
ax_gain_evo_orig.set_ylim(3000 - 1, 20000 + 1)
ax_gain_evo_orig.set_yticks([3000, 5000, 10000, 20000])
ax_gain_evo_orig.set_yticklabels(['3000', '$5000$', '$10000$', '$20000$'])
ax_gain_evo_orig.set_yscale('log')
setup_evolution_axes_orig(ax_gain_evo_orig, 'Cardioid Modulation', 'Hz')

phase_orig = theta_evolution_angles_orig - 0.5*np.sin(2*theta_evolution_angles_orig)
ax_phase_evo_orig.plot(theta_evolution_angles_orig, phase_orig, color=colors_orig['tab:purple'])
ax_phase_evo_orig.set_yticks([0, np.pi/2, np.pi, 3*np.pi/2, 2*np.pi])
ax_phase_evo_orig.set_yticklabels(['0', '$\pi/2$', '$\pi$', '$3\pi/2$', '$2\pi$'])
ax_phase_evo_orig.set_ylim(-0.1, 2*np.pi + 0.1)
setup_evolution_axes_orig(ax_phase_evo_orig, 'Speaker Phase Model (Illustrative)', 'Phase (rad)')

fig.suptitle(f'Original Analysis of Rotating Speaker (LP+HS Model)\nSpeaker shaft = {R_SHAFT} m, dia = {S_SPEAKER_INCH:.1f}", P at {P_COORD[0]} m', fontsize=16, y=0.99)
fig.tight_layout(rect=[0, 0.02, 1, 0.96])
# --- END OF ORIGINAL SCRIPT'S PLOTTING ---


# --- START OF NEW 4x3 FIGURE AND PLOTS (Frequency Response Focus - FAUST MODEL) ---
fig_new = plt.figure(figsize=(12, 10.5))
gs_new = gridspec.GridSpec(4, 3, figure=fig_new, hspace=0.75, wspace=0.3)
colors_new = mcolors.TABLEAU_COLORS

ax_master_freq_response_anim_new = fig_new.add_subplot(gs_new[0:3, 0:3])
ax_master_freq_response_anim_new.set_title('Animated Combined Filter Frequency Response')
ax_master_freq_response_anim_new.set_xlabel('Frequency (Hz)')
ax_master_freq_response_anim_new.set_ylabel('Magnitude (dB)')
ax_master_freq_response_anim_new.set_xscale('log')
ax_master_freq_response_anim_new.set_xlim(FREQ_MIN, FREQ_MAX)
ax_master_freq_response_anim_new.set_ylim(-50, 5) 
ax_master_freq_response_anim_new.grid(True, which="both", ls=":", alpha=0.7)
line_master_freq_response_new, = ax_master_freq_response_anim_new.plot([], [], color='tab:green', lw=2)
text_theta_display_new = ax_master_freq_response_anim_new.text(0.02, 0.98, '',
                                                              transform=ax_master_freq_response_anim_new.transAxes,
                                                              ha='left', va='top', fontsize=10,
                                                              bbox=dict(boxstyle='round,pad=0.3', fc='w', alpha=0.8))

# Calculate min_fc_hs1/2 for static plots (representing most filtered state for each)
if S_SPEAKER > 0:
    min_fc_hs1_static_plot = C_SOUND / (2 * S_SPEAKER)
else:
    min_fc_hs1_static_plot = FREQ_MAX
min_fc_hs1_static_plot = np.clip(min_fc_hs1_static_plot, FREQ_MIN, FREQ_MAX)

min_fc_hs2_static_plot = 3 * min_fc_hs1_static_plot
min_fc_hs2_static_plot = np.clip(min_fc_hs2_static_plot, FREQ_MIN, FREQ_MAX)

# Max comb delay for static plot
_, ps1_evo_new_static, ps2_evo_new_static = calculate_general_distances(
    np.linspace(0, 2 * np.pi, N_POINTS_EVOLUTION), R_SHAFT, S_SPEAKER, P_COORD
)
max_comb_delay_s_new = 0.0
if not (np.any(np.isnan(ps1_evo_new_static)) or np.any(np.isnan(ps2_evo_new_static))):
    comb_delay_s_evo_new = np.abs(ps1_evo_new_static - ps2_evo_new_static) / C_SOUND
    if np.any(comb_delay_s_evo_new > 0):
        max_comb_delay_s_new = np.max(comb_delay_s_evo_new)

def setup_static_freq_axes_new(ax, title):
    ax.set_title(title, fontsize=10)
    ax.set_xlabel('Freq (Hz)', fontsize=9)
    ax.set_ylabel('Mag (dB)', fontsize=9)
    ax.set_xscale('log')
    ax.set_xlim(FREQ_MIN, FREQ_MAX)
    ax.set_ylim(-25, 5) 
    ax.grid(True, which="both", ls=":", alpha=0.7)
    ax.tick_params(axis='both', which='major', labelsize=8)

ax_hs1_static_new = fig_new.add_subplot(gs_new[3, 0])
hs1_static_resp_new = get_faust_highshelf1_response(min_fc_hs1_static_plot, FAUST_HS_GAIN_LIN, FS_SAMPLE_RATE)
ax_hs1_static_new.plot(freq_axis_global, hs1_static_resp_new, color=colors_new['tab:orange'])
setup_static_freq_axes_new(ax_hs1_static_new, f'Filter 1 (Most Filtered)\n$f_c={min_fc_hs1_static_plot:.0f}$ Hz, G={FAUST_HS_GAIN_DB:.1f}dB')

ax_hs2_static_new = fig_new.add_subplot(gs_new[3, 1])
hs2_static_resp_new = get_faust_highshelf1_response(min_fc_hs2_static_plot, FAUST_HS_GAIN_LIN, FS_SAMPLE_RATE)
ax_hs2_static_new.plot(freq_axis_global, hs2_static_resp_new, color=colors_new['tab:pink'])
setup_static_freq_axes_new(ax_hs2_static_new, f'Filter 2 (Most Filtered)\n$f_c={min_fc_hs2_static_plot:.0f}$ Hz, G={FAUST_HS_GAIN_DB:.1f}dB')

ax_cf_static_new = fig_new.add_subplot(gs_new[3, 2])
if max_comb_delay_s_new > EPSILON :
    cf_static_resp_new = get_comb_filter_response(max_comb_delay_s_new)
    ax_cf_static_new.plot(freq_axis_global, cf_static_resp_new, color=colors_new['tab:cyan'])
    setup_static_freq_axes_new(ax_cf_static_new, f'Comb (Most Filtered)\nDelay={max_comb_delay_s_new*1000:.2f}ms')
else:
    ax_cf_static_new.plot(freq_axis_global, np.zeros_like(freq_axis_global), color=colors_new['tab:cyan'])
    setup_static_freq_axes_new(ax_cf_static_new, 'Comb (No Effect or Max Delay=0)')
    ax_cf_static_new.set_ylim(-5,5)

interval_new_ms = 50 
fps_new = 1000 / interval_new_ms

def init_animation_new_fig():
    line_master_freq_response_new.set_data([], [])
    text_theta_display_new.set_text('')
    return (line_master_freq_response_new, text_theta_display_new)

def update_animation_new_fig(frame_num):
    theta_anim = (frame_num / N_FRAMES_ANIM) * 2 * np.pi

    # --- Faust Model Filter Calculations ---
    if S_SPEAKER > 0:
        current_min_fc_hs1 = C_SOUND / (2 * S_SPEAKER)
    else: # If speaker has no size, no directivity effect from this term
        current_min_fc_hs1 = FREQ_MAX 
    current_min_fc_hs1 = np.clip(current_min_fc_hs1, FREQ_MIN, FREQ_MAX)

    # HS1 parameters
    lfo_hs1 = np.abs(np.sin(theta_anim)) 
    base_hs1 = current_min_fc_hs1 / FREQ_MAX # Ratio must be > 0
    fc_hs1 = FREQ_MAX * (base_hs1 ** lfo_hs1)
    fc_hs1 = np.clip(fc_hs1, FREQ_MIN, FREQ_MAX)
    resp_hs1_db = get_faust_highshelf1_response(fc_hs1, FAUST_HS_GAIN_LIN, FS_SAMPLE_RATE, freq_axis_global)

    # HS2 parameters
    current_min_fc_hs2 = 3 * current_min_fc_hs1
    current_min_fc_hs2 = np.clip(current_min_fc_hs2, FREQ_MIN, FREQ_MAX)
    lfo_hs2 = 0.5 - 0.5 * np.cos(theta_anim) 
    base_hs2 = current_min_fc_hs2 / FREQ_MAX # Ratio must be > 0
    fc_hs2 = FREQ_MAX * (base_hs2 ** lfo_hs2)
    fc_hs2 = np.clip(fc_hs2, FREQ_MIN, FREQ_MAX)
    resp_hs2_db = get_faust_highshelf1_response(fc_hs2, FAUST_HS_GAIN_LIN, FS_SAMPLE_RATE, freq_axis_global)
    
    # Comb filter calculation 
    current_d_comb_s_new = 0.0
    _, current_ps1_new, current_ps2_new = calculate_general_distances(theta_anim, R_SHAFT, S_SPEAKER, P_COORD)
    if not (np.isnan(current_ps1_new) or np.isnan(current_ps2_new)):
        current_d_comb_s_new = np.abs(current_ps1_new - current_ps2_new) / C_SOUND
    resp_cf_db_new = get_comb_filter_response(current_d_comb_s_new)

    total_resp_db_new = resp_hs1_db + resp_hs2_db + resp_cf_db_new
    line_master_freq_response_new.set_data(freq_axis_global, total_resp_db_new)
    
    text_theta_display_new.set_text(
        f'$\Theta = {theta_anim*180/np.pi:.0f}^\circ$\n'
        f'Faust HS1: $f_c = {fc_hs1:.0f}$ Hz\n'
        f'Faust HS2: $f_c = {fc_hs2:.0f}$ Hz\n'
        f'(Gain for both HS: {FAUST_HS_GAIN_DB:.1f} dB)\n'
        f'Comb $d = {current_d_comb_s_new*1000:.2f}$ ms'
    )
    return (line_master_freq_response_new, text_theta_display_new)

ani_new = animation.FuncAnimation(fig_new, update_animation_new_fig, frames=N_FRAMES_ANIM,
                                  init_func=init_animation_new_fig, blit=True, interval=interval_new_ms)

fig_new.suptitle(f'Combined Filter Frequency Response\n'
                 f'Shaft: {R_SHAFT}m, Speaker: {S_SPEAKER_INCH:.1f}", P: {P_COORD}m, Faust HS Gain: {FAUST_HS_GAIN_DB:.1f}dB',
                 fontsize=14, y=0.99)
fig_new.tight_layout(rect=[0, 0, 1, 0.95])
# --- END OF NEW 4x3 FIGURE AND PLOTS ---

# --- Create Ressources Directory and Save GIFs ---
if not os.path.exists(RESSOURCES_DIR):
    os.makedirs(RESSOURCES_DIR)
    print(f"Created directory: {RESSOURCES_DIR}")

path_orig_gif = os.path.join(RESSOURCES_DIR, "speaker_animation.gif")
print(f"Saving original model animation to {path_orig_gif} (this may take a moment)...")
try:
    ani_orig.save(path_orig_gif, writer='pillow', fps=fps_orig)
    print("Original model animation saved successfully.")
except Exception as e:
    print(f"Error saving original model animation: {e}")
    print("Make sure you have 'pillow' installed (pip install pillow).")

path_new_gif = os.path.join(RESSOURCES_DIR, "frequency_response_animation.gif")
print(f"Saving new Faust model frequency response animation to {path_new_gif} (this may take a moment)...")
try:
    ani_new.save(path_new_gif, writer='pillow', fps=fps_new)
    print("New Faust model animation saved successfully.")
except Exception as e:
    print(f"Error saving new Faust model animation: {e}")
    print("Make sure you have 'pillow' installed (pip install pillow).")

plt.close(fig)
plt.close(fig_new)

print(f"\n--- Static Plot Parameters (Most Filtered State for each filter individually) ---")
print(f"Base (min) fc for Faust HS1 (when its LFO=1): {min_fc_hs1_static_plot:.0f} Hz")
print(f"Base (min) fc for Faust HS2 (when its LFO=1): {min_fc_hs2_static_plot:.0f} Hz")
print(f"Max comb delay for static plot: {max_comb_delay_s_new*1000:.2f} ms")
print(f"Faust HS Gain (for both): {FAUST_HS_GAIN_DB:.1f} dB (Linear: {FAUST_HS_GAIN_LIN})")