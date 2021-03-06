import os, time
from datetime import datetime
import tensorflow as tf
import numpy as np
import pickle as pkl

from model import *
from gp import *
from mnist import *
from celeba import *
from mnist2 import *
from plotting import *
from utils import *

##################################
# params
##################################
flags = tf.app.flags
FLAGS = flags.FLAGS
# models
flags.DEFINE_integer('HIDDEN_SIZE', 128, 'hidden unit size of network')
flags.DEFINE_string('MODEL_TYPE', 'NP', "{NP|ANP|SNP|ASNP}")
flags.DEFINE_string('ATTENTION_TYPE', 'multihead',
                    "{uniform|laplace|dot_product|multihead}")
flags.DEFINE_float('beta', 1.0, 'weight to kl loss term')
flags.DEFINE_integer('n_default', 25, 'temporal attention size')
flags.DEFINE_boolean('pq_trainable', True, 'pq query trainable or not')
# dataset
flags.DEFINE_string('dataset','mnist','{gp|mnist|celeba}')
flags.DEFINE_integer('case', 1, '{1|2|3}')
flags.DEFINE_integer('MAX_CONTEXT_POINTS', 500,
                     'max context size at each time-steps')
flags.DEFINE_integer('LEN_SEQ', 20, 'sequence length')
flags.DEFINE_integer('LEN_GIVEN', 10, 'given context length')
flags.DEFINE_integer('LEN_GEN', 10, 'generalization test sequence length')
# gp dataset
flags.DEFINE_float('l1_min', 0.7, 'l1 initial boundary')
flags.DEFINE_float('l1_max', 1.2, 'l1 initial boundary')
flags.DEFINE_float('l1_vel', 0.03, 'l1 kernel parameter dynamics')
flags.DEFINE_float('sigma_min', 1.0, 'sigma initial boundary')
flags.DEFINE_float('sigma_max', 1.6, 'sigma initial boundary')
flags.DEFINE_float('sigma_vel', 0.05, 'sigma kernel parameter dynamics')
# mnist dataset
flags.DEFINE_integer('canvas_size', 42, 'canvas size')
flags.DEFINE_float('speed_min', 3.0, 'mnist minimum dynamics')
flags.DEFINE_float('speed_max', 3.0, 'mnist maximum dynamics')
# training
flags.DEFINE_integer('TRAINING_ITERATIONS', 1000000, 'training iteration')
flags.DEFINE_integer('PLOT_AFTER', 1000, 'plot iteration')
flags.DEFINE_integer('batch_size', 16, 'batch size')
flags.DEFINE_string('log_folder', 'logs', 'log folder')
# for rebuttal
flags.DEFINE_integer('recent_K', 0, 'how many the past contexts are stored')

##################################
# additional settings
##################################
# mkdir
log_dir = os.path.join(FLAGS.log_folder,
                       datetime.now().strftime("%m-%d,%H:%M:%S.%f"))
create_directory(log_dir)


summary_ops = []
tf.reset_default_graph()

# tensorboard text
hyperparameters = [tf.convert_to_tensor([key, str(value)])
                for key,value in tf.flags.FLAGS.flag_values_dict().items()]
summary_text = tf.summary.text('hyperparameters',tf.stack(hyperparameters))

# tensorboard image
if FLAGS.dataset=='gp':
    tb_img = tf.placeholder(tf.float32,
                    [None, 480*(FLAGS.LEN_SEQ+FLAGS.LEN_GEN), 640, 3])
elif FLAGS.dataset in ['mnist', 'celeba']:
    # target, context, prediction, uncertainty
    tb_img = tf.placeholder(tf.float32,
                    [None,
                     480*(FLAGS.LEN_SEQ+FLAGS.LEN_GEN),
                     480*4, 3])
else:
    raise NotImplemented

summary_img = tf.summary.image('results',tb_img)

# beta placeholder
beta = tf.placeholder(tf.float32, shape=[])

# temporal model or not
if (FLAGS.MODEL_TYPE == 'NP') or (FLAGS.MODEL_TYPE == 'ANP'):
    temporal=False
else:
    temporal=True

if FLAGS.MODEL_TYPE == 'SNP2':
    temporal=False

##################################
# dataset
##################################
# Train dataset
if FLAGS.dataset == 'gp':
    dataset_train = GPCurvesReader(
        batch_size=FLAGS.batch_size, max_num_context=FLAGS.MAX_CONTEXT_POINTS,
        len_seq=FLAGS.LEN_SEQ, len_given=FLAGS.LEN_GIVEN,
        len_gen=FLAGS.LEN_GEN,
        l1_min=FLAGS.l1_min, l1_max=FLAGS.l1_max, l1_vel=FLAGS.l1_vel,
        sigma_min=FLAGS.sigma_min, sigma_max=FLAGS.sigma_max,
        sigma_vel=FLAGS.sigma_vel, temporal=temporal,
        case=FLAGS.case)
elif FLAGS.dataset == 'mnist':
    dataset_train = MnistReader(
        batch_size=FLAGS.batch_size, max_num_context=FLAGS.MAX_CONTEXT_POINTS,
        len_seq=FLAGS.LEN_SEQ, len_given=FLAGS.LEN_GIVEN,
        len_gen=FLAGS.LEN_GEN, canvas_size=FLAGS.canvas_size,
        speed_min=FLAGS.speed_min, speed_max=FLAGS.speed_max,
        temporal=temporal,
        case=FLAGS.case)
elif FLAGS.dataset == 'celeba':
    dataset_train = CelebaReader(
        batch_size=FLAGS.batch_size, max_num_context=FLAGS.MAX_CONTEXT_POINTS,
        len_seq=FLAGS.LEN_SEQ, len_given=FLAGS.LEN_GIVEN,
        len_gen=FLAGS.LEN_GEN, canvas_size=FLAGS.canvas_size,
        speed_min=FLAGS.speed_min, speed_max=FLAGS.speed_max,
        temporal=temporal,
        case=FLAGS.case)
else:
    raise NotImplemented
#data_train = dataset_train.generate_temporal_curves(seed=2345)
data_train = dataset_train.generate_temporal_curves(seed=None)

# Test dataset
if FLAGS.dataset == 'gp':
    dataset_test = GPCurvesReader(
        batch_size=FLAGS.batch_size, max_num_context=FLAGS.MAX_CONTEXT_POINTS,
        testing=True,
        len_seq=FLAGS.LEN_SEQ, len_given=FLAGS.LEN_GIVEN,
        len_gen=FLAGS.LEN_GEN,
        l1_min=FLAGS.l1_min, l1_max=FLAGS.l1_max, l1_vel=FLAGS.l1_vel,
        sigma_min=FLAGS.sigma_min, sigma_max=FLAGS.sigma_max,
        sigma_vel=FLAGS.sigma_vel, temporal=temporal,
        case=FLAGS.case)
elif FLAGS.dataset == 'mnist':
    dataset_test = MnistReader(
        batch_size=FLAGS.batch_size, max_num_context=FLAGS.MAX_CONTEXT_POINTS,
        testing=True,
        len_seq=FLAGS.LEN_SEQ, len_given=FLAGS.LEN_GIVEN,
        len_gen=FLAGS.LEN_GEN, canvas_size=FLAGS.canvas_size,
        speed_min=FLAGS.speed_min, speed_max=FLAGS.speed_max,
        temporal=temporal,
        case=FLAGS.case)
elif FLAGS.dataset == 'celeba':
    dataset_test = CelebaReader(
        batch_size=FLAGS.batch_size, max_num_context=FLAGS.MAX_CONTEXT_POINTS,
        testing=True,
        len_seq=FLAGS.LEN_SEQ, len_given=FLAGS.LEN_GIVEN,
        len_gen=FLAGS.LEN_GEN, canvas_size=FLAGS.canvas_size,
        speed_min=FLAGS.speed_min, speed_max=FLAGS.speed_max,
        temporal=temporal,
        case=FLAGS.case)
else:
    raise NotImplemented
data_test = dataset_test.generate_temporal_curves(seed=1234)

##################################
# model
##################################

# Sizes of the layers of the MLPs for the encoders and decoder
# The final output layer of the decoder outputs two values, one for the mean
# and one for the variance of the prediction at the target location
latent_encoder_output_sizes = [FLAGS.HIDDEN_SIZE]*4
num_latents = FLAGS.HIDDEN_SIZE
deterministic_encoder_output_sizes= [FLAGS.HIDDEN_SIZE]*4
if FLAGS.dataset == 'celeba':
    decoder_output_sizes = [FLAGS.HIDDEN_SIZE]*2 + [6]
else:
    decoder_output_sizes = [FLAGS.HIDDEN_SIZE]*2 + [2]

# NP - equivalent to uniform attention
if FLAGS.MODEL_TYPE == 'NP':
  attention = Attention(rep='identity', output_sizes=None,
                        att_type='uniform')
# ANP
elif FLAGS.MODEL_TYPE == 'ANP':
  attention = Attention(rep='mlp', output_sizes=[FLAGS.HIDDEN_SIZE]*2,
                        att_type=FLAGS.ATTENTION_TYPE)
# SNP
elif FLAGS.MODEL_TYPE == 'SNP':
  attention = Attention(rep='identity', output_sizes=None,
                        att_type='uniform')
# SNP with attention
elif FLAGS.MODEL_TYPE == 'SNP2':
  attention = Attention(rep='mlp', output_sizes=[FLAGS.HIDDEN_SIZE]*2,
                        att_type=FLAGS.ATTENTION_TYPE)
# SNP with temporal attention
elif 'ASNP' in FLAGS.MODEL_TYPE:
#elif FLAGS.MODEL_TYPE == 'ASNP':
  attention = Attention(rep='mlp', output_sizes=[FLAGS.HIDDEN_SIZE]*2,
                        att_type=FLAGS.ATTENTION_TYPE)
else:
  raise NameError("MODEL_TYPE not among ['NP,'ANP,'SNP','ASNP']")

# Define the model
if temporal:
    if FLAGS.MODEL_TYPE == 'SNP':
        model = TemporalLatentModel(latent_encoder_output_sizes, num_latents,
                                decoder_output_sizes,
                                deterministic_encoder_output_sizes,attention,
                                beta, FLAGS.dataset)
    elif FLAGS.MODEL_TYPE == 'ASNP':
        model = AttentiveTemporalLatentModel(latent_encoder_output_sizes,
                                num_latents,
                                decoder_output_sizes,
                                deterministic_encoder_output_sizes,
                                attention, beta, FLAGS.n_default,
                                FLAGS.dataset, FLAGS.canvas_size,ice_type='all')
    # ablation-only with rnn
    elif FLAGS.MODEL_TYPE == 'ASNP2':
        model = AttentiveTemporalLatentModel(latent_encoder_output_sizes,
                                num_latents,
                                decoder_output_sizes,
                                deterministic_encoder_output_sizes,
                                attention, beta, FLAGS.n_default,
                                FLAGS.dataset, FLAGS.canvas_size,ice_type='rnn')
    # ablation-only with att
    elif FLAGS.MODEL_TYPE == 'ASNP3':
        model = AttentiveTemporalLatentModel(latent_encoder_output_sizes,
                                num_latents,
                                decoder_output_sizes,
                                deterministic_encoder_output_sizes,
                                attention, beta, FLAGS.n_default,
                                FLAGS.dataset, FLAGS.canvas_size,ice_type='att')
else:
    # ASNP-W
    if FLAGS.MODEL_TYPE == 'SNP2':
        model = TemporalLatentModel(latent_encoder_output_sizes, num_latents,
                                decoder_output_sizes,
                                deterministic_encoder_output_sizes,attention,
                                beta, FLAGS.dataset, recent_K=FLAGS.recent_K)
    else:
        model = LatentModel(latent_encoder_output_sizes, num_latents,
                        decoder_output_sizes,
                        deterministic_encoder_output_sizes, attention,
                        beta, FLAGS.dataset)

# Reconstruction
_, _, log_prob, kl, loss, debug_metrics = model(data_train.query,
                                    data_train.num_total_points,
                                    data_train.num_context_points,
                                    data_train.target_y,
                                    inference=True)

# Generation
mu, sigma, t_nll, _, _, debug_metrics = model(data_test.query,
                                        data_test.num_total_points,
                                        data_test.num_context_points,
                                        data_test.target_y,
                                        inference=False)

if not 'ASNP' in FLAGS.MODEL_TYPE:
    [log_p, log_p_list, log_p_w_con, log_p_wo_con,
    mse, mse_list, mse_w_con, mse_wo_con, log_p_seen,
     log_p_unseen] = debug_metrics
else:
    [log_p, log_p_list, log_p_w_con, log_p_wo_con,
    mse, mse_list, mse_w_con, mse_wo_con, log_p_seen,
     log_p_unseen, drnn_h_x_list] = debug_metrics

# tensorboard writer
summary_ops.append(tf.summary.scalar('ELBO/loss', loss))
summary_ops.append(tf.summary.scalar('ELBO/log_prob', log_prob))
summary_ops.append(tf.summary.scalar('ELBO/kl', kl))
summary_ops.append(tf.summary.scalar('TargetNLL/Nll', log_p))
summary_ops.append(tf.summary.scalar('TargetNLL/NllWithCont', log_p_w_con))
summary_ops.append(tf.summary.scalar('TargetNLL/NllWithoutCont',
                                     log_p_wo_con))
for t in range(len(log_p_list)):
    summary_ops.append(tf.summary.scalar('TargetNLL/NllSeen_'+str(t), 
        log_p_seen))
    summary_ops.append(tf.summary.scalar('TargetNLL/NllUnseen_'+str(t), 
        log_p_unseen))
    summary_ops.append(tf.summary.scalar('TargetNLL/nll_'+str(t),
                       log_p_list[t]))
summary_ops.append(tf.summary.scalar('TargetMSE/Mse', mse))
summary_ops.append(tf.summary.scalar('TargetMSE/MseWithCont', mse_w_con))
summary_ops.append(tf.summary.scalar('TargetMSE/MseWithoutCont', mse_wo_con))
for t in range(len(mse_list)):
    summary_ops.append(tf.summary.scalar('TargetMSE/mse_'+str(t),
                       mse_list[t]))

##################################
# training
##################################
# Set up the optimizer and train step
optimizer = tf.train.AdamOptimizer(1e-4)
train_step = optimizer.minimize(loss)
init = tf.initialize_all_variables()

# Saver setting
saver = tf.train.Saver()
checkpoint_path = os.path.join(log_dir, "model")
ckpt = tf.train.get_checkpoint_state(log_dir)

# get param tensor names
param_names = get_param_names(mu, sigma, data_test.query,
                              data_test.num_total_points,
                              data_test.num_context_points,
                              data_test.target_y)
with open(os.path.join(log_dir,'names.pickle'), 'wb') as f:
    pkl.dump(param_names, f)

# learning log
log_file = open(os.path.join(log_dir,'learning_log'), 'w')

# Train and plot
with tf.Session() as sess:
  merged_summary = tf.summary.merge(summary_ops)
  writer = tf.summary.FileWriter(log_dir)
  writer.add_summary(sess.run(summary_text))
  st = time.time()
  sess.run(init)

  for it in range(FLAGS.TRAINING_ITERATIONS):

    sess.run([train_step], feed_dict={beta:FLAGS.beta})

    # Plot the predictions in `PLOT_AFTER` intervals
    if it % FLAGS.PLOT_AFTER == 0:

      if not 'ASNP' in FLAGS.MODEL_TYPE:
          [summ, log_prob_, kl_, loss_, target_nll_, pred_y, std_y,
           query, target_y, hyperparams] = sess.run([merged_summary,
                                                 log_prob, kl, loss, t_nll,
                                                 mu, sigma,
                                                 data_test.query,
                                                 data_test.target_y,
                                                 data_test.hyperparams],
                                                 feed_dict={
                                                 beta:FLAGS.beta}
                                                 )
      else:
          [summ, log_prob_, kl_, loss_, target_nll_, pred_y, std_y,
           query, target_y, hyperparams, h_x_list] = sess.run([merged_summary,
                                                 log_prob, kl, loss, t_nll,
                                                 mu, sigma,
                                                 data_test.query,
                                                 data_test.target_y,
                                                 data_test.hyperparams,
                                                 drnn_h_x_list],
                                                 feed_dict={
                                                 beta:FLAGS.beta}
                                                 )

      writer.add_summary(summ, global_step=it)

      log_line = ['It: {}'.format(it),
                  'time: {}'.format(time.time()-st),
                  'loss: {}'.format(loss_),
                  'log_prob: {}'.format(log_prob_),
                  'kl: {}'.format(kl_),
                  'target_nll: {}'.format(target_nll_)]
      log_line = ','.join(log_line)
      log_file.writelines(log_line+'\n')
      print(log_line)

      with open(os.path.join(log_dir,'data'+str(it).zfill(7)+'.pickle'),
                'wb') as f:
          pkl.dump(pred_y, f)
          pkl.dump(std_y, f)
          pkl.dump(query, f)
          pkl.dump(target_y, f)
          pkl.dump(hyperparams, f)
          if 'ASNP' in FLAGS.MODEL_TYPE:
              pkl.dump(h_x_list, f)

      # Plot the prediction and the context
      plot_data = reordering(query, target_y, pred_y, std_y, temporal)
      if FLAGS.dataset=='gp':
          if not 'ASNP' in FLAGS.MODEL_TYPE:
            img = plot_functions_1d(FLAGS.LEN_SEQ, FLAGS.LEN_GIVEN,
                                    FLAGS.LEN_GEN,
                                    log_dir, plot_data, hyperparams)
          else:
            img = plot_functions_1d(FLAGS.LEN_SEQ, FLAGS.LEN_GIVEN,
                                    FLAGS.LEN_GEN,
                                    log_dir, plot_data, hyperparams,
                                    h_x_list)
          writer.add_summary(sess.run(summary_img,
              feed_dict={tb_img:np.reshape(img,
                         [-1,480*(FLAGS.LEN_SEQ+FLAGS.LEN_GEN),640,3])}),
              global_step=it)
      elif FLAGS.dataset in ['mnist', 'celeba', 'mnist2']:
          if not 'ASNP' in FLAGS.MODEL_TYPE:
            img = plot_functions_2d(FLAGS.LEN_SEQ, FLAGS.LEN_GIVEN,
                                    FLAGS.LEN_GEN, FLAGS.canvas_size,
                                    log_dir, plot_data, hyperparams,
                                    )
          else:
            img = plot_functions_2d(FLAGS.LEN_SEQ, FLAGS.LEN_GIVEN,
                                    FLAGS.LEN_GEN, FLAGS.canvas_size,
                                    log_dir, plot_data, hyperparams,
                                    h_x_list)
          writer.add_summary(sess.run(summary_img,
               feed_dict={tb_img:np.reshape(img,
                          [-1,
                           480*(FLAGS.LEN_SEQ+FLAGS.LEN_GEN),
                           480*4, 3])}),
               global_step=it)
      else:
          raise NotImplemented

      # store model
      saver.save(sess, checkpoint_path, global_step=it)

log_file.close()
