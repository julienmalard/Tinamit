import numpy as np
import matplotlib
import matplotlib.pyplot as plt

from collections import Counter

from matplotlib.colors import LinearSegmentedColormap
from mpl_toolkits.axes_grid1 import make_axes_locatable

from tinamit.Análisis.Sens.behavior import find_best_behavior
from tinamit.Geog.Geog import _gen_clrbar_dic

import multiprocessing as mp
import time


def verif_sens(método, tipo_egr, egr, mapa_paráms, p_soil_class):
    if tipo_egr == "forma" or tipo_egr == 'superposition':
        final_sens = {método: {tipo_egr: {p_name: {b_name: {bp_gof: {para: {f_name: np.asarray([f_val[id][i]
                                                                                                for i, id in enumerate(
                p_soil_class)])
                                                                            for f_name, f_val in
                                                                            val.items()} if para in mapa_paráms else val
                                                                     for para, val in bp_gof_val['mu_star'].items()}
                                                            for bp_gof, bp_gof_val in b_val.items()}
                                                   for b_name, b_val in p_val.items()}
                                          for p_name, p_val in egr[tipo_egr].items()}}}


    elif tipo_egr == "paso_tiempo":
        final_sens = {método: {tipo_egr: {p_name: {para: {paso: np.asarray([paso_val[id][i]
                                                                            for i, id in enumerate(p_soil_class)])
                                                          for paso, paso_val in
                                                          val.items()} if para in mapa_paráms else val
                                                   for para, val in p_val['mu_star'].items()}
                                          for p_name, p_val in egr[tipo_egr].items()}}}
    elif tipo_egr == "promedio":
        final_sens = {método: {tipo_egr: {p_name: {para: np.asarray([val[id][i]
                                                                     for i, id in enumerate(
                p_soil_class)]) if para in mapa_paráms else val
                                                   for para, val in p_val['mu_star'].items()}
                                          for p_name, p_val in egr[tipo_egr].items()}}}
    else:
        raise Exception('Not defined type!')

    return final_sens

def _single_poly(samples, i, f_simul_arch, gaurdar):
    fited_behav = {i: {j: {} for j in range(samples)}}
    for j in range(samples):
        print(f'this is {j}-th sample')
        behav = np.load(f_simul_arch + f"f_simul_{j}.npy").tolist()
        fited_behav[i][j] = find_best_behavior(behav, trans_shape=i)
    if gaurdar is not None:
        np.save(gaurdar + f'fit_beh_poly-{i}', fited_behav)

def analy_behav_by_dims(method, samples, dims, f_simul_arch, dim_arch=None, gaurdar=None):

    if dim_arch is None:
        if method == 'morris':
            fited_behav = {i: {j: {} for j in range(samples)} for i in range(dims)}
            for j in range(samples):
                print(f'this is {j}-th sample')
                behav = np.load(f_simul_arch + f"f_simul_{j}.npy").tolist()
                for i in range(dims):
                    fited_behav[i][j] = find_best_behavior(behav, trans_shape=i)
                    print(f'processing {i} poly')
            if gaurdar is not None:
                np.save(gaurdar + 'fited_behav', fited_behav)

        elif method == 'fast':
            pool = mp.Pool(processes=10)

            results = []
            for i in range(dims):
                if i not in [34, 144, 176, 186]:
                    continue
                print(f'Processing {i} poly')
                results.append(pool.apply_async(_single_poly, args=(samples, i, f_simul_arch, gaurdar,)))

            [result.wait() for result in results]
            # output = [p.get() for p in results]
            print("finished")


    else:
        fited_behav = {}
        aic_behav = {}
        for i in range(dims):
            count_fited_behav_by_poly = []
            # polynal_fited_behav = np.load("D:\Thesis\pythonProject\localuse\Dt\Mor\Mor_home\\f_simul\\dict_fited_behav.npy")[i]
            polynal_fited_behav = np.load(dim_arch).tolist()[i]
            for j in range(samples):
                count_fited_behav_by_poly.extend([key for key, val in polynal_fited_behav[j]])

            count_fited_behav_by_poly = [k for k, v in Counter(count_fited_behav_by_poly).items() if
                                         v / len(count_fited_behav_by_poly) > 0.1]
            fited_behav.update({i: count_fited_behav_by_poly})

            aic_poly = {k: [] for k in count_fited_behav_by_poly}
            for j in range(samples):
                # behav = np.load(
                #     f"D:\Thesis\pythonProject\localuse\Dt\Mor\Mor_home\\f_simul\corrected_bf\\new_spp\\new_f_simul_sppf_simul_{j}.npy").tolist()
                behav = np.load(f_simul_arch + f"f_simul_{j}.npy").tolist()

                for k in count_fited_behav_by_poly:
                    aic_poly[k].append(behav[k]['gof']['aic'][0, i])
                print(f'processing sample-{j} for poly-{i}')
            aic_behav.update({i: {k: np.average(v) for k, v in aic_poly.items()}})

        if gaurdar is not None:
            np.save(gaurdar + 'fited_behav', fited_behav)
            np.save(gaurdar + 'aic_behav', aic_behav)


def gen_counted_behavior(fited_behav_arch, gaurdar=None):
    fited_behaviors = np.load(fited_behav_arch).tolist()
    counted_all_behaviors = []
    for i in range(len(fited_behaviors)):
        counted_all_behaviors.extend(fited_behaviors[i])
    counted_all_behaviors = set(counted_all_behaviors)
    if gaurdar is not None:
        np.save(gaurdar + 'counted_all_behaviors', counted_all_behaviors)
    else:
        return counted_all_behaviors


def gen_alpha(fited_behav_arch, patt):
    fited_behav = np.load(fited_behav_arch).tolist()
    d_alpha = {i: [] for i in fited_behav}
    for poly, behavs in fited_behav.items():
        if patt in behavs:
            d_alpha[poly] = 1.0
        else:
            d_alpha[poly] = 0.0
    return np.asarray([a for p, a in d_alpha.items()])


def map_sens(geog, metodo, tipo_egr, para_name, data, midpoint, path, alpha=None, behav=None, paso=None, ids=None):
    vars_interés = {tipo_egr: {
        'col': ['#f8fef7', '#e7fde5', '#d6fcd2', '#c5fbc0', '#b4f9ad', '#b4f9ad', '#5ff352',
                '#5395a0', '#4a8590', '#42767f', '#39666e', '#30565d', '#28474c', '#1f373c',
                '#ffe6e6', '#ffcccc', '#ffb3b3', '#ff9999', '#ff8080', '#ff2f2f', '#ff0808'
                ],
        'escala_núm': [min(data), max(data)]}}

    # clr_bar_dic = {'green': ['#e6fff2', '#80ffbf'] , # '#33ff99', '#00cc66', '#006633'],
    #                'blue': ['#80dfff', '#00bfff', '#1ac6ff', '#00ace6', '#007399'],
    #                'red': ['#ff8000', '#ff8c1a', '#ff8000']}

    clr_bar_dic = {'green': ['#e6fff2', '#b3ffd9'],
                   'blue': ['#80ff9f', '#80ff80', '#9fff80', '#bfff80', '#dfff80', '#ffff80', '#ffdf80', '#ff8080'],
                   'red': ['#ff0000', '#ff0000']}

    unid = 'Morris Sensitivity Index'

    for v, d in vars_interés.items():
        # for j in [0, 5, 15, 20]:
        #     geog.dibujar(archivo=path + f'old-{j}', valores=data[j], título=f'Soil salinity old paso-{j}',
        #                  unidades='Soil salinity level',
        #                  colores=d['col'], ids=ids)  # for azahr

        # paso
        # ll = [0, 5, 15, 20]
        # for i in ll:
        #     max_val = max(data[f'paso_{i}'])
        #     if max_val > 11:
        #         data[f'paso_{i}'][np.where(data[f'paso_{i}'] > 11)] = 11
        #         max_val = 12
        #     geog.dibujar(archivo=path + f'{i}-{para_name}', valores=data[f'paso_{i}'],
        #                  título=f"Mor-{para_name[: 5]}-Timestep-{i} to WTD",
        #                  unidades=unid, colores=d['col'], ids=ids, midpoint=midpoint, clr_bar_dic=clr_bar_dic,
        #                  escala_num=(0, max_val))

        # mean val
        max_val = max(data)
        if max_val > 11:
            data[np.where(data > 11)] = 11
            max_val = 12
        geog.dibujar(archivo=path + f'mean-{para_name}', valores=data,
                     título=f"{metodo[:2]}-{para_name}-to WTD-Mean", midpoint=midpoint, clr_bar_dic=clr_bar_dic,
                     unidades=unid, colores=d['col'], ids=ids, escala_num=(0, max_val))

        # beahv
        # for bpprm in data:  # "D:\Thesis\pythonProject\localuse\Dt\Mor\map\\spp\\aic\\{bpprm}-{behav}-{para_name}" #f"D:\Thesis\pythonProject\localuse\Dt\Mor\map\spp\\bppprm\\bpprm-{behav}-{para_name}"
        #     max_val = max(data[bpprm])
        #     if max_val > 11:
        #         data[bpprm][np.where(data[bpprm] > 11)] = 11
        #         max_val = 12
        #
        #     geog.dibujar(archivo=path + f"{metodo[:2]}-{para_name[: 5]}-{behav}-{bpprm}",  # midpoint=midpoint,
        #                  valores=data[bpprm],
        #                  título=f"{metodo[:2].capitalize()}-{para_name[0].capitalize()+para_name[1: 5]}-{behav[0].capitalize()+ behav[1:]}-{bpprm}",
        #                  alpha=alpha, unidades=unid, colores=d['col'], ids=ids, midpoint=midpoint,
        #                  clr_bar_dic=clr_bar_dic,
        #                  escala_num=(0, max_val)
        #                  )


def map_rank(fst_cut, snd_cut, maxi, row_labels, col_labels, data, title, y_label, archivo, ax=None, cbar_kw={},
             cbarlabel="Sensitivity Index", **kwargs):
    '''

    Parameters
    ----------
    row_labels:  A list or array of length N with the labels for the rows
    ["cucumber", "tomato", "lettuce", "asparagus", "potato", "wheat", "barley"]
    col_labels: A list or array of length M with the labels for the columns
    ["Farmer Joe", "Upland Bros.", "Smith Gardening", "Agrifun", "Organiculture", "BioGoods Ltd.", "Cornylee Corp."]
    data: A 2D numpy array of shape (N,M)
    np.array([[0.8, 2.4, 2.5, 3.9, 0.0, 4.0, 0.0],
            [2.4, 0.0, 4.0, 1.0, 2.7, 0.0, 0.0],
            [1.1, 2.4, 0.8, 4.3, 1.9, 4.4, 0.0],
            [0.6, 0.0, 0.3, 0.0, 3.1, 0.0, 0.0],
            [0.7, 1.7, 0.6, 2.6, 2.2, 6.2, 0.0],
            [1.3, 1.2, 0.0, 0.0, 0.0, 3.2, 5.1],
            [0.1, 2.0, 0.0, 1.4, 0.0, 1.9, 6.3]])

    Optional arguments:
        ax         : A matplotlib.axes.Axes instance to which the heatmap
                     is plotted. If not provided, use current axes or
                     create a new one.
        cbar_kw    : A dictionary with arguments to
                     :meth:`matplotlib.Figure.colorbar`.
        cbarlabel  : The label for the colorbar
    All other arguments are directly passed on to the imshow call.

    cmap="Wistia", cmap="magma_r" , cmap=plt.get_cmap("PiYG", 7) yellow-black, cmap="PuOr" brown
    vmin=0, vmin=-1, vmax=1
    cbar_kw=dict(ticks=np.arange(-3, 4),

    Returns
    -------

    '''
    if not ax:
        fig, ax = plt.subplots()

    # clr_bar_dic = {'green': ['#e6fff2', '#80ffbf', '#33ff99', '#00cc66', '#006633'],
    #                'blue': ['#80dfff', '#00bfff', '#1ac6ff', '#00ace6', '#007399'],
    #                'red': ['#ff8000', '#ff8c1a', '#ff8000']}

    clr_bar_dic = {'green': ['#e6fff2', '#b3ffd9'],
                   'blue': ['#80ff9f', '#80ff80', '#9fff80', '#bfff80', '#dfff80', '#ffff80', '#ffdf80', '#ff8080'],
                   'red': ['#ff0000', '#ff0000']}

    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="1.5%", pad=0.05)
    # fig.colorbar(im, cax=cax)

    # Plot the heatmap and # Create colorbar
    if fst_cut < data.max() < snd_cut:
        dic_c = _gen_clrbar_dic(fst_cut=fst_cut, snd_cut=None, maxi=maxi, first_set=clr_bar_dic['green'],
                                second_set=clr_bar_dic['blue'], third_set=clr_bar_dic['red'])
        mapa_color = LinearSegmentedColormap('mapa_color', dic_c)
        im = ax.imshow(data, mapa_color)
        cbar = fig.colorbar(im, cax=cax, ticks=[0, fst_cut, data.max()])
        # cbar = ax.figure.colorbar(im, ax=cax, ticks=[0, fst_cut, data.max()], **cbar_kw)
        cbar.ax.set_yticklabels(['0', f'Screnning threshold, {fst_cut}', f'maximum_val_{data.max()}'], fontsize=3)

    elif data.max() > snd_cut:
        if data.max() > 11:
            data[np.where(data > 11)] = 11

        dic_c = _gen_clrbar_dic(fst_cut=fst_cut, snd_cut=snd_cut, maxi=11, first_set=clr_bar_dic['green'],
                                second_set=clr_bar_dic['blue'], third_set=clr_bar_dic['red'])
        mapa_color = LinearSegmentedColormap('mapa_color', dic_c)
        im = ax.imshow(data, mapa_color)
        cbar = fig.colorbar(im, cax=cax, ticks=[0, fst_cut, snd_cut, 12])
        cbar.ax.set_yticklabels(
            ['0', f'Screnning threshold, {fst_cut}', '+ 10 High sensitivity zone', '+ 10 High sensitivity zone'],
            fontsize=3)

    elif data.max() < fst_cut:
        dic_c = _gen_clrbar_dic(fst_cut=None, snd_cut=None, maxi=maxi, first_set=clr_bar_dic['green'],
                                second_set=clr_bar_dic['blue'], third_set=clr_bar_dic['red'])
        mapa_color = LinearSegmentedColormap('mapa_color', dic_c)
        im = ax.imshow(data, mapa_color)
        cbar = fig.colorbar(im, cax=cax, ticks=[0, data.max()])
        # cbar = ax.figure.colorbar(im, ax=cax, ticks=[0, data.max()], **cbar_kw)
        cbar.ax.set_yticklabels(['0', f'maximum_val_{data.max()}'], fontsize=3)

    cbar.ax.set_ylabel(cbarlabel, rotation=-90, va="bottom", fontsize=5)
    ax.tick_params(width=0.1)
    cbar.ax.tick_params(width=0.1)

    # We want to show all ticks...
    ax.set_xticks(np.arange(data.shape[1]))
    ax.set_yticks(np.arange(data.shape[0]))
    # ... and label them with the respective list entries.
    ax.set_xticklabels(col_labels, fontsize=3)
    ax.set_yticklabels(row_labels, fontsize=4)

    # Let the horizontal axes labeling appear on top.
    ax.tick_params(top=True, bottom=False, labeltop=True, labelbottom=False)

    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=-30, ha="right",
             rotation_mode="anchor")

    # Turn spines off and create white grid.
    for edge, spine in ax.spines.items():
        spine.set_visible(False)

    ax.set_xticks(np.arange(data.shape[1] + 1) - .5, minor=True)
    ax.set_yticks(np.arange(data.shape[0] + 1) - .5, minor=True)
    ax.grid(which="minor", color="w", linestyle='-', linewidth=0.5)
    ax.tick_params(which="minor", bottom=False, left=False)

    # escala_num = (np.nanmin(data), np.nanmax(data))
    #
    # vals_norm = (data - escala_num[0]) / (escala_num[1] - escala_num[0])
    # norm = matplotlib.colors.Normalize(vmin=0, vmax=escala_num[-1])

    def _annotate_rankmap(fst_cut=fst_cut, snd_cut=snd_cut, im=im, valfmt="{x:.2f}", txtclr=["white", "black", 'white'],
                          **textkw):
        """
        A function to annotate a rankmap.

        Arguments:
            im         : The AxesImage to be labeled.
        Optional arguments:
            data       : Data used to annotate. If None, the image's data is used.
            valfmt     : The format of the annotations inside the heatmap.
                         This should either use the string format method, e.g.
                         "$ {x:.2f}", or be a :class:`matplotlib.ticker.Formatter`.
            textcolors : A list or array of two color specifications. The first is
                         used for values below a threshold, the second for those
                         above.
            threshold  : Value in data units according to which the colors from
                         textcolors are applied. If None (the default) uses the
                         middle of the colormap as separation.

        Further arguments are passed on to the created text labels.
        valfmt="{x:d}" (integer format), valfmt="{x:.1f}",
        **textkw: size=7, fontweight="bold",
        """

        # Normalize the threshold to the images color range.
        fst_cut = im.norm(fst_cut)
        snd_cut = im.norm(snd_cut)

        # Set default alignment to center, but allow it to be
        # overwritten by textkw.
        kw = dict(horizontalalignment="center",
                  verticalalignment="center")
        kw.update(textkw)

        # Get the formatter in case a string is supplied
        if isinstance(valfmt, str):
            valfmt = matplotlib.ticker.StrMethodFormatter(valfmt)

        # Loop over the data and create a `Text` for each "pixel".
        # Change the text's color depending on the data.
        texts = []
        for i in range(data.shape[0]):
            for j in range(data.shape[1]):
                kw.update(color=txtclr[fst_cut < im.norm(data[i, j]) < snd_cut])
                text = im.axes.text(j, i, valfmt(data[i, j], None), **kw)
                texts.append(text)
        return texts

    _annotate_rankmap(im=im, size=0.1)
    # matplotlib.ticker.FuncFormatter(
    #     "{:.2f}".format(data).replace("0.", ".").replace("0.00", "")))
    # Loop over data dimensions and create text annotations.

    ax.set_title(title, fontsize=10, y=1.5)
    ax.set_ylabel(y_label, fontsize=5)
    # plt.title(title, y=1.5)

    fig.tight_layout(h_pad=1)
    fig.savefig(archivo, dpi=1000)
    plt.close()
