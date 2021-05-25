import pandas as pd
import random, os, sys
import numpy as np



#### Add path for python import  #######################################
path_repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + "/"
print("path_repo_root", path_repo_root)
sys.path.append( path_repo_root)
from util_feature import  save, load_function_uri, load 		
########################################################################


folder     = 'raw/'
df         = pd.read_csv(folder+'train_csv.csv', delimiter=',')
df_test     = pd.read_csv(folder+'test_csv.csv', delimiter=',')

"""
	Rename columns for train and test 
"""
df      = df.rename(columns = {'39':'age' , ' State-gov':'workclass', ' 77516':'final_weight', ' Bachelors':'education', ' 13':'education-num', ' Never-married':'marital-status', ' Adm-clerical':'occupation', ' Not-in-family':'relationship', ' White':'race', ' Male':'sex', ' 2174':'capital-gain', ' 0':'capital-loss', ' 40':'hours-per-week', ' United-States':'native-country', ' <=50K':'status'})
df.name = "df"
df_test = df_test.rename(columns = {'25':'age' , ' Private':'workclass', ' 226802':'final_weight', ' 11th':'education', ' 7':'education-num', ' Never-married':'marital-status', ' Machine-op-inspct':'occupation', ' Own-child':'relationship', ' Black':'race', ' Male':'sex', ' 0':'capital-gain', ' 0.1':'capital-loss', ' 40':'hours-per-week', ' United-States':'native-country', ' <=50K.':'status'})
df_test.name = "df_test"



def pd_cleanup(df, col, pars):
  df.drop(['education'], axis=1, inplace = True)
  df.replace(" ?",np.NaN,inplace=True)

  # Converting the value of the target column to a 0-1
  if (df.name == "df"):
    df.status = [ 0 if each == " <=50K" else 1 for each in df.status]
  else:
    df.status = [ 0 if each == " <=50K." else 1 for each in df.status]

  df["id"]=[i+1 for i in range(len(df))]
  return df




def pd_normalize_quantile(df, col=['age', 'final_weight', 'capital-gain', 'capital-loss', 'hours-per-week'], pars={}):
  """
     Processor for DSA@
  """
  df      = df[col]
  num_col = col

  sparse_col         = pars.get('colsparse', ['capital-gain', 'capital-loss'] )


  # Find IQR and implement to numerical and sparse columns separately
  Q1  = df.quantile(0.25)
  Q3  = df.quantile(0.75)
  IQR = Q3 - Q1
  pars_new={}
  for col in num_col:
    
	
	
	######  When it runs for testing, it will go into the if block because it will use the saved boundaries.
	
	##### Grab previous computed params
    if pars.get(col, None) is not None:
        saved_bounds = pars.get(col, None)
        lower_bound_sparse = saved_bounds.get("lower_bound_sparse",None)
        upper_bound_sparse = saved_bounds.get("upper_bound_sparse", None)
        lower_bound        = saved_bounds.get("lower_bound", None)
        upper_bound        = saved_bounds.get("upper_bound", None)
    else:
        lower_bound_sparse=None
        upper_bound_sparse=None
        lower_bound =None
        upper_bound=None
		
    if col in sparse_col:
      nonsparse_data = pd.DataFrame(df[df[col] != df[col].mode()[0]][col])

      if lower_bound_sparse is not None:
        pass
      else:
          if nonsparse_data[col].quantile(0.25) < df[col].mode()[0]: #Unexpected case
            lower_bound_sparse = nonsparse_data[col].quantile(0.25)
          else:
            lower_bound_sparse = df[col].mode()[0]

      if upper_bound_sparse is not None:
        pass
        
      else:
          if nonsparse_data[col].quantile(0.75) < df[col].mode()[0]: #Unexpected case
            upper_bound_sparse = df[col].mode()[0]
          else:
            upper_bound_sparse = nonsparse_data[col].quantile(0.75)


      number_of_outliers = len(df[(df[col] < lower_bound_sparse) | (df[col] > upper_bound_sparse)][col])

      if number_of_outliers > 0:
        df.loc[df[col] < lower_bound_sparse, col] = lower_bound_sparse * 0.75 #--> MAIN DF CHANGED
        df.loc[df[col] > upper_bound_sparse, col] = upper_bound_sparse * 1.25 # --> MAIN DF CHANGED

    else:

      if lower_bound is not None or upper_bound is not None :
        pass
      else:
        lower_bound = df[col].quantile(0.25) - 1.5 * IQR[col]
        upper_bound = df[col].quantile(0.75) + 1.5 * IQR[col]

        df[col] = np.where(df[col] > upper_bound, 1.25 * upper_bound, df[col])
        df[col] = np.where(df[col] < lower_bound, 0.75 * lower_bound, df[col])
    

    colnew   = [ t + "_norm" for t in df.columns ]
	
    				
	
	######	Each column has its own boundries. So save boundries seperately.
	
    pars_new[col]={'lower_bound' : lower_bound, 'upper_bound': upper_bound,
                'lower_bound_sparse' : lower_bound_sparse, 'upper_bound_sparse' : upper_bound_sparse
                }

				
	######  If we do not reset the values here, the previous column values will be assigned as saved boundaries for the next iteration.	
    lower_bound=None
    upper_bound=None
    lower_bound_sparse=None
    upper_bound_sparse =None


  dfnew    = df
  encoder_model = None
    
  ###################################################################################
  if 'path_features_store' in pars and 'path_pipeline_export' in pars:
      #pass
      #save_features(df, 'dfcat_encoder', pars['path_features_store'])
      #save(colnew,    pars['path_pipeline_export']  + "/colnum_encoder_model.pkl" )
      save(pars_new,  pars['path_pipeline_export']   + "/colnum_quantile_norm_new.pkl" )
   


  col_pars = {}
  col_pars['model']    = encoder_model
  col_pars['pars']     = pars_new
  col_pars['cols_new'] = {
    'colnum_normalize_quantile' :  colnew  ### list
  }

  #dfnew    = df.drop(["status"],axis=1)
  return dfnew,  col_pars



###############################################################################
##### Train processing ########################################################
df             = pd_cleanup(df, col=None, pars=None)
df_, col_pars  = pd_normalize_quantile(df,  col=['age', 'final_weight', 'capital-gain', 'capital-loss', 'hours-per-week'] , pars={} )
df[df_.columns]= df_



feature_tr = df.drop(["status"],axis=1)
target_tr  = df[["status","id"]]
feature_tr.to_csv( "train/features.csv", index=False)
target_tr.to_csv(  "train/target.csv",index=False)

features = dict(method='zip',archive_name='features.csv')  
target = dict(method='zip',archive_name='target.csv')
feature_tr.to_csv('train/features.zip', index=False, compression=features) 
target_tr.to_csv('train/target.zip', index=False,compression=target)



#### to save parameters
pars = col_pars['pars']


##### Test processing ############################################################
df_test    = pd_cleanup(df_test, col=None, pars=None)

df_test_,_ = pd_normalize_quantile(df_test,
                  col  = ['age', 'final_weight', 'capital-gain', 'capital-loss', 'hours-per-week'],
                  pars = pars)
df_test[df_test_.columns]=df_test_
feature_test = df_test.drop(["status"],axis=1)
target_test  = df_test[["status","id"]]
feature_test.to_csv('test/features.zip', index=False, compression=features)
target_test.to_csv('test/target.zip', index=False,compression=target)
