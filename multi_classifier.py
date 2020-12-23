# pylint: disable=C0321,C0103,E1221,C0301,E1305,E1121,C0302,C0330
# -*- coding: utf-8 -*-
"""
https://www.kaggle.com/tapioca/multiclass-lightgbm

https://medium.com/@nitin9809/lightgbm-binary-classification-multi-class-classification-regression-using-python-4f22032b36a2



All in one file config
  python multi_classifier.py  train
  python multi_classifier.py  check
  python multi_classifier.py  predict


"""
import warnings, copy, os, sys
warnings.filterwarnings('ignore')

###################################################################################
from source import run_train


####################################################################################
###### Path ########################################################################
print( os.getcwd())
root = os.path.abspath(os.getcwd()).replace("\\", "/") + "/"
print(root)

dir_data  = os.path.abspath( root + "/data/" ) + "/"
dir_data  = dir_data.replace("\\", "/")
print(dir_data)


def global_pars_update(model_dict,  data_name, config_name):
    m                      = {}
    model_name             = model_dict['model_pars']['model_class']
    m['path_config_model'] = root + f"/{config_file}"
    m['model_class']       = config_name

    m['path_data_train']   = f'data/input/{data_name}/train/'
    m['path_data_test']    = f'data/input/{data_name}/test/'

    m['path_model']        = f'data/output/{data_name}/{model_name}/'
    m['path_output_pred']  = f'data/output/{data_name}/pred_{config_name}/'
    m['n_sample']          = model_dict['data_pars'].get('n_sample', 5000)

    model_dict[ 'global_pars'] = m
    return model_dict


def os_get_function_name():
    import sys
    return sys._getframe(1).f_code.co_name


####################################################################################
config_file     = "multi_classifier.py"
config_default  = 'multi_lightgbm'



colid   = 'pet_id'
coly    = 'pet_category'
coldate = ['issue_date','listing_date']
colcat  = ['color_type','condition']
colnum  = ['length(m)','height(cm)','X1','X2'] # ,'breed_category'
colcross= ['condition', 'color_type','length(m)', 'height(cm)', 'X1', 'X2']  # , 'breed_category'


cols_input_type_1 = {  "coly"   :   coly
                    ,"colid"  :   colid
                    ,"colcat" :   colcat
                    ,"colnum" :   colnum
                    ,"coltext" :  []
                    ,"coldate" :  []
                    ,"colcross" : colcross
                   }





####################################################################################
##### Params########################################################################
def multi_lightgbm(path_model_out="") :
    """
       multiclass
    """
    data_name         = f"multiclass"     ### in data/input/
    model_name        = 'LGBMClassifier'
    n_sample          = 6000

    def post_process_fun(y):
        ### After prediction is done
        return  int(y)

    def pre_process_fun_multi(y):
        ### Before the prediction is done
        return  int(y)


    model_dict = {'model_pars': {
        'model_path'       : path_model_out

        ### LightGBM API model  ########################################
        ,'model_class': model_name    ## ACTUAL Class name for model_sklearn.py
        ,'model_pars'       : {'objective': 'multiclass','num_class':4,'metric':'multi_logloss',
                                'learning_rate':0.03,'boosting_type':'gbdt'

                              }

        ### After prediction  ##########################################
        , 'post_process_fun' : post_process_fun
        , 'pre_process_pars' : {'y_norm_fun' :  pre_process_fun_multi ,
                                
        ### Pipeline for data processing.
        'pipe_list': [
            {'uri': 'source/preprocessors.py::pd_coly',                 'pars': {}, 'cols_family': 'coly',       'cols_out': 'coly',           'type': 'coly'         },
            {'uri': 'source/preprocessors.py::pd_colnum_bin',           'pars': {}, 'cols_family': 'colnum',     'cols_out': 'colnum_bin',     'type': ''             },
            {'uri': 'source/preprocessors.py::pd_colnum_binto_onehot',  'pars': {}, 'cols_family': 'colnum_bin', 'cols_out': 'colnum_onehot',  'type': ''             },
            {'uri': 'source/preprocessors.py::pd_colcat_bin',           'pars': {}, 'cols_family': 'colcat',     'cols_out': 'colcat_bin',     'type': ''             },
            {'uri': 'source/preprocessors.py::pd_colcat_to_onehot',     'pars': {}, 'cols_family': 'colcat_bin', 'cols_out': 'colcat_onehot',  'type': ''             },
            {'uri': 'source/preprocessors.py::pd_colcross',             'pars': {}, 'cols_family': 'colcross',   'cols_out': 'colcross_pair_onehot',  'type': 'cross'}
        ],

        },
        },

      'compute_pars': { 'metric_list': ['roc_auc_score','accuracy_score'],
                        'probability': True,  ### output probability for classifier
                      },

      'data_pars': {
          'n_sample' : n_sample,

          ### columns from raw file, based on data type, #############
          'cols_input_type' : cols_input_type_1,

          ### family of columns for MODEL  ########################################################
          #  "colnum", "colnum_bin", "colnum_onehot", "colnum_binmap",  #### Colnum columns
          #  "colcat", "colcat_bin", "colcat_onehot", "colcat_bin_map",  #### colcat columns
          #  'colcross_single_onehot_select', "colcross_pair_onehot",  'colcross_pair',  #### colcross columns
          #  'coldate',
          #  'coltext',
          'cols_model_group': [ 'colnum_bin','colcat_bin']


          ### Filter data rows   #####################################
         ,'filter_pars': { 'ymax' : 5 ,'ymin' : -1 }

         }
      }

    ##### Filling Global parameters    #############################################################
    model_dict        = global_pars_update(model_dict, data_name, config_name=os_get_function_name() )
    return model_dict







#####################################################################################
########## Profile data #############################################################
def data_profile(path_data_train="", path_model="", n_sample= 5000):
   from source.run_feature_profile import run_profile
   run_profile(path_data   = path_data_train,
               path_output = path_model + "/profile/",
               n_sample    = n_sample,
              )



###################################################################################
########## Preprocess #############################################################
def preprocess(config=None, nsample=None):
    config_name  = config  if config is not None else config_default
    mdict        = globals()[config_name]()
    m            = mdict['global_pars']
    print(mdict)

    from source import run_preprocess2, run_preprocess
    run_preprocess2.run_preprocess(config_name=  config_name,
                                   path_data         =  m['path_data_train'],
                                   path_output       =  m['path_model'],
                                   path_config_model =  m['path_config_model'],
                                   n_sample          =  nsample if nsample is not None else m['n_sample'],
                                   mode              =  'run_preprocess')


##################################################################################
########## Train #################################################################
def train(config=None, nsample=None):

    config_name  = config  if config is not None else config_default
    mdict        = globals()[config_name]()
    m            = mdict['global_pars']
    print(mdict)

    from source import run_train
    run_train.run_train(config_name=  config_name,
                        path_data         =  m['path_data_train'],
                        path_output       =  m['path_model'],
                        path_config_model =  m['path_config_model'],
                        n_sample          =  nsample if nsample is not None else m['n_sample'])


###################################################################################
######### Check data ##############################################################
def check():
   pass




####################################################################################
####### Inference ##################################################################
def predict(config=None, nsample=None):
    config_name  = config  if config is not None else config_default
    mdict        = globals()[config_name]()
    m            = mdict['global_pars']
    print(m)

    from source import run_inference2
    run_inference2.run_predict(config_name,
                            path_model  = m['path_model'],
                            path_data   = m['path_data_test'],
                            path_output = m['path_output_pred'],
                            pars={'cols_group': mdict['data_pars']['cols_input_type'],
                                  'pipe_list': mdict['model_pars']['pre_process_pars']['pipe_list']},
                            n_sample    = nsample if nsample is not None else m['n_sample'])


def run_all():
    data_profile()
    preprocess()
    train()
    check()
    predict()




###########################################################################################################
###########################################################################################################
"""
python  multi_classifier.py  data_profile
python  multi_classifier.py  preprocess
python  multi_classifier.py  train
python  multi_classifier.py  check
python  multi_classifier.py  predict
python  multi_classifier.py  run_all
"""
if __name__ == "__main__":
    import fire
    fire.Fire()
    
