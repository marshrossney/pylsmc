import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from sys import argv

from params import *
import domain as dom
import extra_info as exi

if algorithm == 'wang_landau':
    import wang_landau as alg
elif algorithm == 'multicanonical':
    import multicanonical as alg
elif algorithm == 'transition':
    import transition_matrix as alg

# What are we plotting?
plottype = argv[1]

plt.rc('text',usetex=True)
font = {'family' : 'serif',
        'size' : 14}
plt.rc('font', **font)
plt.rcParams['axes.linewidth'] = 2

# Colours to distinguish between subdomains
mkrs = ['bo-', 'go-']


##########################
## Cuts and diffusivity ##
##########################
if plottype == 'diff':

    # ---------------- #
    #  Make the plots  #
    # ---------------- #
    fig, ax = plt.subplots()
    ax.set_title("Cuts histogram")
    ax.set_xlabel(r"$\mu \times \beta/N$")
    ax.set_ylabel("Counts through the cut")
    ax.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
    
    fig2, ax2 = plt.subplots()
    ax2.set_title("Diffusivity")
    ax2.set_xlabel(r"$\mu \times \beta/N$")
    ax2.set_ylabel("Diffusivity")
    ax2.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
    
    fig3, ax3 = plt.subplots()
    ax3.set_title("Log of diffusivity")
    ax3.set_xlabel(r"$\mu \times \beta/N$")
    ax3.set_ylabel("log(Diffusivity)")
    ax3.ticklabel_format(style='sci', axis='y', scilimits=(0,0))

    # ------------------------- #
    #  Iterate over subdomains  #
    # ------------------------- #
    for s in range(Ns):

        # Get file names to load
        input_files = alg.file_names('output', s, 0)
        extra_input_files = exi.file_names('output', s, 0)

        # Load mu domain
        mu_bins = dom.get_local_mu_bins(s) * B / float(Natoms)

        # Load input files
        hist = np.loadtxt(input_files['h'])
        cuts = np.loadtxt(extra_input_files['cu'])
        cuts = cuts * dom.subdom[s]['bin_width']

        # Formula given in Tian et a. (2014), though coefficient is arbitrary in this case
        cuts = 0.5*cuts
        diffusivity = np.pi / exi.cuts_step * (cuts**2) / (hist**2)

        # The edge bins are not well estimated with the cuts method implemented
        diffusivity[0] = diffusivity[1] + 0.25*(diffusivity[1] - diffusivity[4])
        diffusivity[-1] = diffusivity[-2] + 0.25*(diffusivity[-2] - diffusivity[-5])
  
        # Take the log so we can more easily see how many O.O.M's it spans
        logD = np.log(diffusivity)
        logD -= np.min(logD)

        # Add this subdomain to plots
        ax.plot(mu_bins, cuts, mkrs[s%2])
        ax2.plot(mu_bins, diffusivity, mkrs[s%2])
        ax3.plot(mu_bins, logD, mkrs[s%2])



############################
## Acceptance probability ##
############################
if plottype == 'ac':

    # ---------------- #
    #  Make the plots  #
    # ---------------- #
    fig, ax = plt.subplots()
    ax.set_title("Acceptance probabilities")
    ax.set_xlabel(r"$\mu \times \beta/N$")
    ax.set_ylabel("Acceptance probability")
    
    Pacc_mean = 0
    Pacc_list = []

    # ------------------------- #
    #  Iterate over subdomains  #
    # ------------------------- #
    for s in range(Ns):

        # Get file names to load
        input_files = alg.file_names('output', s, 0)
        extra_input_files = exi.file_names('output', s, 0)

        # Load input files
        hist = np.loadtxt(input_files['h'])
        accepts = np.loadtxt(extra_input_files['ac'])
        
        # Add acceptance probability to list to be plotted later
        Pacc = accepts / hist
        Pacc = Pacc[1:-1] # ignore edge bins
        Pacc_list.append(Pacc)
        Pacc_mean += np.mean(Pacc)

    # Get the average acceptance probability
    Pacc_mean = Pacc_mean / float(Ns)

    # ------------------------------- #
    #  Iterate over subdomains again  #
    # ------------------------------- #
    for s in range(Ns):
        
        # Load mu domain
        mu_bins = dom.get_local_mu_bins(s)[1:-1] * B / float(Natoms)

        # Add this subdomain to plot
        ax.plot(mu_bins, Pacc_list[s] - Pacc_mean, mkrs[s%2])


###################################
## Average step sizes (mu and E) ##
###################################
if plottype == 'step':

    # ---------------- #
    #  Make the plots  #
    # ---------------- #
    fig, ax = plt.subplots()
    ax.set_title("Average step sizes in mu")
    ax.set_xlabel(r"$\mu \times \beta/N$")
    ax.set_ylabel(r"$\delta \mu \times \beta/N$")
    
    fig2, ax2 = plt.subplots()
    ax2.set_title("Average step sizes in E")
    ax2.set_xlabel(r"$\mu \times \beta/N$")
    ax2.set_ylabel(r"$\delta E \times \beta/N$")

    # ------------------------- #
    #  Iterate over subdomains  #
    # ------------------------- #
    for s in range(Ns):

        # Get file names to load
        input_files = alg.file_names('output', s, 0)
        extra_input_files = exi.file_names('output', s, 0)

        # Load mu domain
        mu_bins = dom.get_local_mu_bins(s) * B / float(Natoms)

        # Load input files
        hist = np.loadtxt(input_files['h'])
        accepts = np.loadtxt(extra_input_files['ac'])
        dmu = np.loadtxt(extra_input_files['dm'])     
        dmu_acc = np.loadtxt(extra_input_files['dma'])     
        dE = np.loadtxt(extra_input_files['de'])     
        dE_acc = np.loadtxt(extra_input_files['dea'])     

        # Get average size by dividing sum by counts
        dmu = dmu / hist
        dmu_acc = dmu_acc / accepts
        dE = dE / hist
        dE_acc = dE_acc / accepts

        # Scale by temperature and N atoms
        dmu = dmu * B / float(Natoms)
        dmu_acc = dmu_acc * B / float(Natoms)
        dE = dE * B / float(Natoms)
        dE_acc = dE_acc * B / float(Natoms)

        # Add this subdomain to plots
        if s == 0:
            ax.plot(mu_bins, dmu, mkrs[0], label="Average step size")
            ax.plot(mu_bins, dmu_acc, mkrs[1], label="Average accepted step size")
            ax2.plot(mu_bins, dE, mkrs[0], label="Average step size")
            ax2.plot(mu_bins, dE_acc, mkrs[1], label="Average accepted step size")
        else:
            ax.plot(mu_bins, dmu, mkrs[0])
            ax.plot(mu_bins, dmu_acc, mkrs[1])
            ax2.plot(mu_bins, dE, mkrs[0])
            ax2.plot(mu_bins, dE_acc, mkrs[1])

    ax.legend()
    ax2.legend()


####################################################
## Size of attempted steps out of the (sub)domain ##
####################################################
if plottype == 'edge':

    # ---------------- #
    #  Make the plots  #
    # ---------------- #
    fig, ax = plt.subplots()
    ax.set_title("Average size of attempted steps out of the (sub)domain")
    ax.set_xlabel("Subdomain")
    ax.set_ylabel(r"$\delta \mu$")

    # Initialise lists
    mean_list = []
    ninetieth_list = []
    bin_width_list = []

    # ------------------------- #
    #  Iterate over subdomains  #
    # ------------------------- #
    for s in range(Ns):

        # Get file names to load
        extra_input_files = exi.file_names('output', s, 0)

        # Load input files
        left = np.loadtxt(extra_input_files['led'])
        right = np.loadtxt(extra_input_files['red'])

        # Mean step size in both directions
        lmean = np.mean(left)
        rmean = np.mean(right)

        # Mean and 90th percentile in direction where they're larger
        if lmean > rmean:
            mean_list.append(lmean)
            ninetieth_list.append( np.percentile(left, 90) )
        else:
            mean_list.append(rmean)
            ninetieth_list.append( np.percentile(right, 90) )

        # Compare with bin width for this subdomain
        bin_width_list.append(dom.subdom[s]['bin_width'])

    
    # Add data from all subdomains to plot
    subdoms = np.arange(Ns)
    ax.plot(subdoms, mean_list, 'g--', label="Mean")
    ax.plot(subdoms, ninetieth_list, 'r--', label="90th percentile")
    ax.plot(subdoms, bin_width_list, 'ko', label="Bin width")
    ax.legend()

    # Want integer tick labels for subdomains
    fig.gca().xaxis.set_major_locator(MaxNLocator(integer=True))


######################################################
## Fine-grained matrix for transition probabilities ##
######################################################
if plottype == 'mini':

    fig, ax = plt.subplots()
    ax.set_title("Probability distribution after %d steps" %exi.minimat_step)
    ax.set_xlabel(r"$\mu \times \beta/N$")
    ax.set_ylabel(r"$\delta \mu \times \beta/N$")

    fig2, ax2 = plt.subplots()
    ax2.set_title("Diffusivity calculated using variance")
    ax2.set_xlabel(r"$\mu \times \beta/N$")
    ax2.set_ylabel("Diffusivity")
    ax2.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
    
    fig3, ax3 = plt.subplots()
    ax3.set_title("Log of diffusivity")
    ax3.set_xlabel(r"$\mu \times \beta/N$")
    ax3.set_ylabel("log(Diffusivity)")
    ax3.ticklabel_format(style='sci', axis='y', scilimits=(0,0))

    for s in range(Ns):

        # Get file names to load
        extra_input_files = exi.file_names('output', s, 0)

        # Load input files
        minimat = np.loadtxt(extra_input_files['mm'])
        minimat = minimat / np.sum(minimat, axis=0)

        # Load mu arrays for bins and minibins
        mu_bins = dom.get_local_mu_bins(s)
        window_width = exi.subdom[s]['win_width']
        mini_mu_bins = np.linspace(0, window_width, exi.minibins_per_window) - 0.5*window_width

        # Ignore overlaps
        l = dom.subdom[s]['l_bin_olap']
        h = -dom.subdom[s]['h_bin_olap']
        if s == Ns-1: h = None # it works
        mu_bins_no_olap = mu_bins[l:h]
        minimat_no_olap = minimat[:,l:h]

        # Add to plot
        im = ax.pcolor(mu_bins_no_olap, mini_mu_bins, minimat_no_olap, cmap='inferno')

        # Add thin white lines to denote bin boundaries
        bin_indices = np.arange(0, exi.minibins_per_window, exi.minibins_per_bin)
        bin_indices += (exi.minibins_per_window - bin_indices[-1])/2
        l_edge = np.ones(exi.bins_per_window) * mu_bins_no_olap[0]
        r_edge = np.ones(exi.bins_per_window) * mu_bins_no_olap[-1]
        ax.plot(l_edge, mini_mu_bins[bin_indices], 'w_')
        ax.plot(r_edge, mini_mu_bins[bin_indices], 'w_')

        # Initialise arrays for first and second moments
        size = len(minimat[0,:])
        mom1 = np.zeros(size)
        mom2 = np.zeros(size)

        # Iterate over windows
        for win in range(size):
        
            # Check simulation has visited all bins
            if np.sum(minimat[:,win]) == 0:
                print "Error: zeros in the matrix diagonal. Unable to compute variance."
                print "Exiting..."
                exit(1)
        
            # Probability distribution and calculation of moments
            P_dist = minimat[:,win] / np.sum(minimat[:,win])
            mom1[win] = np.dot( exi.subdom[s]['win_info'][win]['bin_mus'],    P_dist)
            mom2[win] = np.dot( exi.subdom[s]['win_info'][win]['bin_mus']**2, P_dist)
    
        # Variance
        var = mom2 - mom1*mom1

        # Convert to diffusivity. Not really necessary since we only care about
        # variations in D, so the coefficient is arbitrary
        diffusivity = var / float(2*exi.minimat_step)

        # The edge bins are not well estimated. Don't bother plotting them.
        # Also don't plot domain edges, even though they're not in an overlap region
        if Ns > 1:
            if s == 0: l = -h
            elif s == Ns-1: h = -l
        else: # above doesn't work
            l = 2
            h = -2
        diffusivity = diffusivity[l:h]
        mu_bins = mu_bins[l:h]
        
        # Take the log so we can more easily see how many O.O.M's it spans
        logD = np.log(diffusivity)
        logD -= np.min(logD)
        
        # Add to diffusivity plots
        ax2.plot(mu_bins, diffusivity, mkrs[s%2])
        ax3.plot(mu_bins, logD, mkrs[s%2])

    
    # Add colorbar and text to plot
    fig.colorbar(im)
    
print "Mu = E(%s) - E(%s)" %(alpha_type, beta_type)

plt.show()


