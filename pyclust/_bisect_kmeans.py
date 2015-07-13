import warnings

import numpy as np
import treelib

from . import _kmeans



def _select_cluster_2_split(membs, sse_arr):
    if np.any(sse_arr > 0):
        clust_id = np.argmax(sse_arr)
        memb_ids = np.where(membs == clust_id)[0]
        return(clust_id,memb_ids)
    else:
        return(0,np.arange(membs.shape[0]))


def add_tree_node(tree, label, X=None, center=None, sse=None, parent=None):
    """
    """
    print("1) center: ", center)
    if (center is None):
        center = np.mean(X, axis=0)
    print("2) center: ", center)
    if (sse is None):
        sse = _kmeans._cal_dist2center(X, center)

    center = list(center)
    datadict = {
        'center': center, 
        'label' : label, 
        'sse'   : sse 
    }
    if (parent is not None):
        tree.create_node(label, label, parent=parent, data=datadict)
    else:
        tree.create_node(label, label, data=datadict)

    return(tree)



def _bisect_kmeans(X, n_clusters, n_trials, max_iter, tol):
    """ Apply Bisecting Kmeans clustering
        to reach n_clusters number of clusters
    """
    membs = np.empty(shape=X.shape[0], dtype=int)
    centers = np.empty(shape=(n_clusters,X.shape[1]), dtype=float)
    sse_arr = -1.0*np.ones(shape=n_clusters, dtype=float)

    ## data structure to store cluster hierarchies
    tree = treelib.Tree()
    tree = add_tree_node(tree, 0, X) 

    km = _kmeans.KMeans(n_clusters=2, n_trials=n_trials, max_iter=max_iter, tol=tol)
    for i in range(1,n_clusters):
        sel_clust_id,sel_memb_ids = _select_cluster_2_split(membs, sse_arr)
        print(sel_clust_id, sel_memb_ids)
        X_sub = X[sel_memb_ids,:]
        km.fit(X_sub)

        ## Updating the clusters & properties
        sse_arr[[sel_clust_id,i]] = km.sse_arr_
        centers[[sel_clust_id,i]] = km.centers_
        tree = add_tree_node(tree, 2*i-1,           \
              	             center=km.centers_[0], \
                             sse=km.sse_arr_[0], \
                             parent= sel_clust_id)

        pred_labels = km.labels_
        print(sel_clust_id)
        pred_labels[np.where(pred_labels == 1)[0]] = 2*i
        pred_labels[np.where(pred_labels == 0)[0]] = 2*i - 1
        #if sel_clust_id == 1:
        #    pred_labels[np.where(pred_labels == 0)[0]] = sel_clust_id
        #    pred_labels[np.where(pred_labels == 1)[0]] = i
        #else:
        #    pred_labels[np.where(pred_labels == 1)[0]] = i
        #    pred_labels[np.where(pred_labels == 0)[0]] = sel_clust_id

        membs[sel_memb_ids] = pred_labels
        print("Bisetcing step %d "%i, membs)

    return(centers, membs, sse_arr)




class BisectKMeans(object):
    """ 
        KMeans Clustering

        Parameters
        -------

        Attibutes
        -------

           

        Methods
        ------- 
           fit()
           predict()
           fit_predict()
    """
    def __init__(self, n_clusters=2, n_trials=10, max_iter=100, tol=0.0001):
        assert n_clusters >= 2, 'n_clusters should be >= 2'
        self.n_clusters = n_clusters
        self.n_trials = n_trials
        self.max_iter = max_iter
        self.tol = tol

    def fit(self, X, y=None):
        """
        """
        self.centers_, self.labels_, self.sse_arr_ = \
            _bisect_kmeans(X, self.n_clusters, self.n_trials, self.max_iter, self.tol)
        
