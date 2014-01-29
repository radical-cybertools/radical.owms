
{
    "stampede.tacc.utexas.edu": {
        "URL"                : "slurm+ssh://stampede.tacc.utexas.edu",
        "filesystem"         : "sftp://stampede.tacc.utexas.edu/",
        "default_queue"      : "normal",
        "python_interpreter" : "/opt/apps/python/epd/7.3.2/bin/python",
        "pre_bootstrap"      : ["module load python"],
        "task_launch_mode"   : "MPIRUN"
    },

    "alamo.futuregrid.org": {
        "URL"                : "pbs+ssh://alamo.futuregrid.org",
        "filesystem"         : "sftp://alamo.futuregrid.org/",
        "default_queue"      : "short",
        "python_interpreter" : "/N/soft/python/2.7/bin/python",
        "pre_bootstrap"      : ["module purge", "module load python", "module load openmpi"],
        "task_launch_mode"   : "MPIRUN",
        "valid_roots"        : ["/N", "/home"]
    },

    "india.futuregrid.org": {
        "URL"                : "pbs+ssh://india.futuregrid.org",
        "filesystem"         : "sftp://india.futuregrid.org/",
        "default_queue"      : "batch",
        "python_interpreter" : "/N/soft/python/2.7/bin/python",
        "pre_bootstrap"      : ["module purge", "module load python", "module load openmpi"],
        "task_launch_mode"   : "MPIRUN",
        "valid_roots"        : ["/N"]
    },

    "sierra.futuregrid.org": {
        "URL"                : "pbs+ssh://sierra.futuregrid.org",
        "filesystem"         : "sftp://sierra.futuregrid.org/",
        "default_queue"      : "batch",
        "python_interpreter" : "/N/soft/python/2.7/bin/python",
        "pre_bootstrap"      : ["module purge", "module load python", "module load openmpi"],
        "task_launch_mode"   : "MPIRUN",
        "valid_roots"        : ["/N"]

    },

    "hotel.futuregrid.org": {
        "URL"                : "pbs+ssh://hotel.futuregrid.org",
        "filesystem"         : "sftp://hotel.futuregrid.org/",
        "default_queue"      : "batch",
        "python_interpreter" : "/soft/python/gnu-4.1/2.7/bin/python",
        "pre_bootstrap"      : ["module purge", "module load python", "module load openmpi"],
        "task_launch_mode"   : "MPIRUN",
        "valid_roots"        : ["/N", "/gpfs"]
    }
}

