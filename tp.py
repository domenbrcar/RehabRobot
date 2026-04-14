# TP Library
#
# Authors: Timotej Gaspar, Miha Denisa

# Importing the module 'quaternion' will throw a warning if we do not have numba.
# I therefore set the warnings filter to 'ignore'.
import warnings
warnings.filterwarnings("ignore")

# Numpy
import numpy as np  # nopep8 - Oterwise the linter complainst for E402

class TP(object):
    """TP Class.

    This is the class that implements the Torque Primitives - TP.
    The class supports both Encoding and Decoding of trajectories.

    Attributes
    ----------
    num_weights : int
        Number of DMP weights.
    a_x : float
        The a_x gain of the DMP.
    a_z : float
        The a_z gain of the DMP.
    b_z : float
        The b_z gain of the DMP.
    c : array like
        The width of the Gaussian bell curves.
    y0 : 1 dimensional array
        The initial position of the DMP
    goal : 1 dimensional array
        The final position of the DMP
    sigma : array of floats
        The values of the Gaussian bell curves.
    num_dof : int
        The number of weights used for estimating the DMP.
    weights_trq : array of floats
        The calulated weights of the TP.

    Parameters
    ----------
    pos_data : np.array or float list
        Data points of the trajectory to encode.
    vel_data : np.array or float list (optional)
        Data points of the trajectory's velocity to encode.
    time : np.array or float list or float
        If the provided time is an array of floats with the same length as the
        `pos_data` parameter, it will be treated as the time samlpes of the trajecoty.
        In case this parameter is a single float, it will be treated as the sample
        time of the trajectory and the time vector will be computed accordingly.
    num_weights : int, optional
        The desired number of weights to estimate the DMP.
    a_z : float, optional
        The a_z gain of the DMP.
    a_x : float, optional
        the a_x gain of the DMP.

    """
    a_x = None
    num_weights = None
    y0 = None
    goal = None
    _num_dof = None
    _d_t = None

    def __str__(self):
        return (f"TP("
                f"  a_x={self.a_x},\n"
                f"  num_weights={self.num_weights},\n"
                f"  y0={self.y0},\n"
                f"  goal={self.goal},\n"
                f"  _num_dof={self._num_dof},\n"
                f"  tau={self.tau}\n"
                f"  c={self.c}\n"
                f"  sigma={self.sigma}\n"
                f"  _d_t={self._d_t}\n"
                f")")


    def __init__(self, trq_data=None, time=None, num_weights=25, a_x=2.0):

        if trq_data is not None:
            # Copy the parameters into the appropriate class attributes
            self.a_x = a_x
            self.num_weights = num_weights
            self._trq_training_data = np.asarray(trq_data)
            self.y0 = self._trq_training_data[0, :]
            
            self.goal = self._trq_training_data[-1, :]
            # We assume that the number of trajectory samples are smaller then the DOF
            self._num_samples = np.max(self._trq_training_data.shape)
            self._num_dof = np.min(self._trq_training_data.shape)

            try:
                if not(len(np.asarray(time).shape)):
                    # If the provided argument is a number we treat is as sample time
                    self._time_vec = np.arange(0, self._num_samples*time, time)
                    self._d_t = time
                else:
                    # If the provided argument an array we treat it as an array
                    # of time stamps
                    if len(time) != self._num_samples:
                        raise Exception("Time stamp vector length does not match the "
                                        "number of samples !!\n"
                                        ">> Num. samples: {0} | Len. time: {1} <<"
                                        .format(self._num_samples, len(time)))
                    else:
                        self._time_vec = np.asarray(time) - time[0]
                        self._d_t = np.mean(np.diff(self._time_vec))
            except Exception as e:
                print('Exception when dealing with the "time" argument:\n{0}'.format(e))
                return

            # Tau equals to the duration of the trajectory
            self.tau = self._time_vec[-1]

            # Prepare the Gaussian kernel functions
            self._prepare_gaussian_kernels()

            # Encode the DMP
            self.__encode_tp()

    def _prepare_gaussian_kernels(self):
        self.c = np.exp(-self.a_x * np.linspace(0, 1, self.num_weights))
        self.sigma = np.square((np.diff(self.c)*0.75))
        self.sigma = np.append(self.sigma, self.sigma[-1])

    def __encode_tp(self):
        y = self._trq_training_data


        # Prepare empty matrices
        ft = np.zeros((self._num_samples, self._num_dof), dtype=np.float32)
        A = np.zeros((self._num_samples, self.num_weights), dtype=np.float32)

        # Define the phase vector
        x = np.exp(-self.a_x * self._time_vec / self.tau)

        # Estimate the forcing term
        for dof in range(self._num_dof):
            ft[:, dof] = y[:, dof]

        for i in range(self._num_samples):
            psi = np.exp(np.divide(-0.5 * np.square(x[i] - self.c), self.sigma))
            A[i, :] = x[i] * np.divide(psi, np.sum(psi))

        # Do linear regression in the least square sense
        self.weights_trq = np.transpose(np.linalg.lstsq(A, ft)[0])

    def __decode_tp(self):
        pass

    def _integrate_step(self, x, y):
        # Phase variable
        # dx = (-a_x * x) / tau
        # x = x + dx * dt
        dx = -self.a_x * x / self.tau
        x = x + dx * self._d_t

        # The weighted sum of the locally weighted regression models
        # psi = exp(-(x - c)^2 / (2 * sigma))
        psi = np.exp(- np.square(x-self.c) /
                     (np.multiply(self.sigma, 2)))

        for dof in range(self._num_dof):
            # Forcing function
            # sum( (w(dof) * x) * psi/sum(psi) )
            fx = sum(np.multiply(
                (np.multiply(self.weights_trq[dof], x)),
                (np.divide(psi, sum(psi)))
            ))

            # Trq
            y[dof] = fx
             
        return x, y

    def decode(self):
        """Function decodes the TP and returns trqs.

        Returns
        ----------
        trq : np.array
            The decoded trqs
        t : np.array
            The time samples for the decoded trqs
        """
        # Initial states
        y = np.asarray(self.y0.copy())
        x = 1

        # Set a limit for the phase
        self.x_min = np.exp(-self.a_x)
        
        # First sample equals y0
        trq = [tuple(y)]
        t = [0]

        # Decode loop
        while x > self.x_min:
            [x, y] = self._integrate_step(x, y)
            trq.append(tuple(y))
            t.append(t[-1]+self._d_t)

        trq = np.asarray(trq)
        return trq, t

    def step_decode(self):
        pass


