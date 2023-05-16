import numpy as np  
import random as ran
from scipy.linalg import lu
import scipy as sc

class Market():
    """ Creats the market environment.
        Works for Models driven by a 1-dimensional Brownian Motion.
    """
    def __init__(self,n,N,sigma,r,s0,T):
        self.n = n
        self.N = N
        self.sigma = sigma
        self.r = r
        self.s0 = s0
        self.T = T
        
    def brownian_motion(self):
        """Computes #N Sample paths of brownian motion

        Args:
            n (int): total number of gridpoints --> look time_grid()
            N (int): total Number of Samples drawn
        """
        t = self.time_grid()
        delta_t = t[1] - t[0]
        dB = np.sqrt(delta_t) * np.random.normal(size=(self.N,self.n - 1))
        B0 = np.zeros(shape=(self.N,1))
        B = np.concatenate((B0,np.cumsum(dB,axis=1)),axis= 1)
        return B
    
    def black_scholes(self):
        """ Creats the Black Scholes Model using the closed Formula
            S(t) = s_0* exp( (r - 0.5*sigma^2)*t + sigma*W_t)

        Returns:
            S (Matrix / Array): Assetprice (row -> Samples, columns -> timepoints)
        """
        t = self.time_grid()
        BB = self.brownian_motion()
        S = np.zeros(shape=(self.N,self.n))
        for j in range(self.N):
            for i in range(self.n):
                S[j,i] = self.s0*np.exp((self.r - 0.5*(self.sigma**2))*t[i] + self.sigma*BB[j,i])
        return S
    
    def bs_phi(self,t,x):
        """performs transformation for time variable t and space Variable x

        Args:
            t (_type_): _description_
            x (_type_): _description_
        """
        return self.s0*np.exp((self.r - 0.5*self.sigma**2)*t + self.sigma*x)
    
    def time_grid(self):
        """Creats a time grid given Time Horizon T and total number of points n.

        Returns:
            Vector / array: timepoints
        """
        time = np.linspace(0,self.T,self.n)
        return time


class European_Options():
    def __init__(self,n,N,K,Assetprice):
        self.K = K
        self.N = N
        self.n = n
        self.S = Assetprice
    
    def Arithmetic_asian_call(self):
        """Computes an European Arithmetic asian Call given the underlying asset S and strike price K

        Returns:
            Vector / Array: Value of the option
        """
        Value = np.zeros(shape = (self.N,))
        for j in range(self.N):
           Value[j] = np.max((1/self.n)* np.sum(self.S[j,:]) - self.K , 0) 
        return Value
    
    def Call(self):
        """ Standard European Call at maturity T (end point)
        
        """
        Value = np.zeros(shape = (self.N,))
        for j in range(self.N):
           Value[j] = np.max(0, self.S[j,-1] - self.K)
        return Value
        
    
    def geo_asian_call(self):
        """Computes an European geometric asian call given the underlying asset S and strike price K

        Returns:
            _Array: Value of option
        """
        Value = np.zeros(shape=(self.N,))
        for j in range(self.N):
           Value[j] = np.max(0, (np.prod(self.S)**(1/self.n)) - self.K) 
        return Value



# Monte Carlo Methods:
class Monte_Carlo():
    """ Class to perfom different Monte Carlo Estimation for financial options
        TODO: Dependencies within init are inconsitent --> Move all non essential (global) variables for each estimator to its respective function
    """
    def __init__(self,N,rv, alpha,r, T,K):
        self.N = N
        self.ov = rv
        self.alpha = alpha
        self.r = r
        self.T = T
        self.K = K
        
        
    def Standard_MC(self):
        """Performes standard Monte Carlo Estimation given N samples of a random variable
            Attantion: SMC is 'discounted' with exp(-r*T).
        Returns:
            Float: estimated expected value
            Float: Variance of the estimator
            Array: Confidence Interval
        """
        p_mc = np.exp(-self.r*self.T)*np.mean(self.ov)
        var_mc = np.var(self.ov)
        percentile = sc.stats.norm.ppf(1 - 0.5*self.alpha)
        upper = p_mc + percentile*np.sqrt(var_mc)/self.N
        lower = p_mc - percentile*np.sqrt(var_mc)/self.N
        ki = np.array([lower, upper])
        return p_mc, var_mc, ki
    
    def SMC(self):
        """Performes standard Monte Carlo Estimation given N samples of a random variable
        
        Returns:
            Float: estimated expected value
            Float: Variance of the estimator
            Array: Confidence Interval
        """
        p_mc = np.mean(self.ov)
        var_mc = np.var(self.ov)
        percentile = sc.stats.norm.ppf(1 - 0.5*self.alpha)
        upper = p_mc + percentile*np.sqrt(var_mc)/self.N
        lower = p_mc - percentile*np.sqrt(var_mc)/self.N
        ki = np.array([lower, upper])
        return p_mc, var_mc, ki
    
    def Anti_thetic_MC(self,env):
        """Performs antithetic estimator for geometric brownian motion
        Uses: Environment --> Asset from Market
        Has to be called with r = T and 
        Returns:
            _type_: _description_
        """
        samples = np.zeros(shape=(self.N,))
        const = 0.5*np.exp(-self.r*self.T)
        for j in range(self.N):
            normal_z = np.random.normal(size=(1,))
            samples[j] = const*(np.max(env.bs_phi(self.T,np.sqrt(self.T)*normal_z) - self.K, 0)+ np.max(env.bs_phi(self.T,-1*np.sqrt(self.T)*normal_z) - self.K, 0))
        p_mc = np.mean(samples)
        var_mc = np.var(samples)
        percentile = sc.stats.norm.ppf(1 - 0.5*self.alpha)
        upper = p_mc + percentile*np.sqrt(var_mc)/self.N
        lower = p_mc - percentile*np.sqrt(var_mc)/self.N
        ki = np.array([lower, upper])
        return p_mc, var_mc, ki   
        
        
        






# Numerical Methods

def boundary_cond(x,L):
    if x<=(L/2):
        y = 2*x
    else:
        y = 2*(L - x)
    return y



def fd_forward_heat(Nx, Nt, T, L, sigma):
    """Computes the forward finite differences approach for u_t = sigma^2 * u_xx

    Args:
        Nx (int): Discretization points for space
        Nt (int): Discretization points for time
        T (float): Time horizon
        L (float): Space horizon
        sigma (float): sigma coeff for heat equation
    """
    # Parameters
    delta_t = T / Nt
    delta_x = L / Nx
    nu = (sigma**2)*(delta_t/(delta_x**2))
    u = np.zeros((Nt+1, Nx+1))
    
    # Boundary conditions (E2)
    for j in range(Nx+1):
        u[0,j] = boundary_cond(j*delta_x, L)
        #u[0,j] = np.sin(j*delta_x)
       
    for i in range(Nt+1):
        u[i,0] = 0
        u[i,-1] = 0
        
    # Recursion for inner points
    for i in range(Nt):
        for j in range(1,Nx):
            u[i+1, j] = nu*u[i, j-1] + (1-2*nu)*u[i, j] + nu*u[i, j+1]
        
    return u

def fd_backward_heat(Nx, Nt, T, L, sigma):
    """performs finite difference scheme for heat eqaution u_t = sigma^2 * u_xx

    Args:
        Nx (int): Discretization points for space
        Nt (int): Discretization points for time
        T (float): Time horizon
        L (float): Space horizon
        sigma (float): sigma coeff for heat equation
    """
    delta_t = T / Nt
    delta_x = L / Nx
    nu = (sigma**2)*(delta_t/(delta_x**2))
    # Loesungsvektor u: Lenght  = N_x - 1
    u = np.zeros((Nx, Nt))
    
    # Matrix B allocation mit dim (N_x, N_x)
    B = np.zeros((Nx-1, Nx-1))
    for i in range(Nx-1):
        B[i,i] = 1+2*nu
        
    for i in range(Nx-2):
        B[i+1,i] = -nu
        B[i,i+1] = -nu

    # L U Decomposition, Jetzt "R-U Zerlegung", da L obere Grenze vom State space ist
    # Gleiche dim wie bei B
    U, R = lu(B,permute_l=True)
    U_inv = np.linalg.inv(U)
    R_inv = np.linalg.inv(R)
    

    
    # Allocate U_0
    for j in range(1, Nx):
        u[j,0] = boundary_cond(j*delta_x,L)
        #u[j,0] = np.sin(j*delta_x)
    # Randbedingungen (fuer t) sind hier egal, da diese konstant 0 sind und mit 0 initialisiert wird
        
    # Rekursion
    for i in range(Nt-1):  
        u_vec = u[1:,i]
        y = U_inv.dot(u_vec)
        u[1:,i+1] = R_inv.dot(y)
    return u
    
       
def real_sol(t, x):
    n = 10000
    u = 0

    for i in range(1,n+1):
        u = u + ((-1)**(i-1))*np.exp((-(2*i-1)**2)*t)*(np.sin((2*i-1)*x))*((2*i-1)**(-2))
    u = (8/np.pi)*u

    return u

def get_max_error(delta_x,u_approx,L):
    """
    get error at t = 0.1 for simple heat equation
    delta_t 
    """
    for j in range(len(u_approx)):
        u_t = real_sol(0.1,L*j/delta_x)
    diff = abs(u_t - u_approx)
    error = diff.max()
    return error
