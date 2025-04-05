import scipy
import numpy as np
import matplotlib.pyplot as plt


FNAME = 'completion_times.tex'

def generate_fake_runtimes(num_runtimes=50):
    """
    Generate fake runtimes for the given number of runs.
    Use a gamma distribution to simulate runtimes.
    Mean 45, min of 30 seconds, going up to 2 mins
    """
    # Generate runtimes using a gamma distribution
    # k = 3, thet= 2
    shape = 3  # shape parameter (k)
    scale = 40  # scale parameter (theta)
    runtimes = np.random.gamma(shape, scale, num_runtimes)
    # runtimes = np.clip(runtimes, 30, 120)  # Ensure all runtimes are between 30 and 120 seconds
    runtimes.sort()
    return runtimes




def save_runtimes_to_tex(runtimes, filename=FNAME):
    np.savetxt(filename, runtimes, fmt='%.2f', delimiter=',')

def plot_runtimes(runtimes):
    plt.figure(figsize=(10, 6))
    plt.hist(runtimes, bins=20, color='blue', alpha=0.7)
    plt.title('Fake Runtimes Histogram')
    plt.xlabel('Runtime (seconds)')
    plt.savefig('fake_runtimes.png')
    plt.show()

if __name__ == "__main__":
    runtimes = generate_fake_runtimes()
    save_runtimes_to_tex(runtimes)
    plot_runtimes(runtimes)


