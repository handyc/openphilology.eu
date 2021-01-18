
from django.http import HttpResponseRedirect, HttpResponseServerError
from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist

from django.urls import reverse

import json
import itertools

import csv, io, re
import diff_match_patch as dmp_module

from .models import UserSettings
from .models import UserFile

from .models import CsvAlignment
from .models import CsvAlignmentList

#from .forms import UploadForm

from .models import Work
from .models import WorkInCollection
from .models import Witness
from .models import WitnessPartition
from .models import Alignment
from .models import AlignmentLog
from .models import Annotation
from .models import AnnotationLog

from .models import Dictionary
from .models import DictionaryEntry
from .models import DictionaryLine

from .models import Ngram
from .models import NgramInWitness

from .forms import UploadForm
from .forms import AlignmentForm

#main_template_location = 'opstudio/main.html'

#nsize_filter=24
nsize_filter=5

search_template="opstudio/search.html"

ngrams_template_location = 'opstudio/ngrams.html'
index_template_location = 'opstudio/index.html'
upload_template_location = 'opstudio/upload.html'

importer_template_location = 'opstudio/importer.html'


reader_template_location = 'opstudio/reader.html'

alignments_template_location = 'opstudio/alignments.html'
annotations_template_location = 'opstudio/annotations.html'
dictionaries_template_location = 'opstudio/dictionaries.html'
ngrams_template_location = 'opstudio/ngrams.html'
embeddings_template_location = 'opstudio/embeddings.html'
sts_template_location = 'opstudio/sts.html'
terminal_template_location = 'opstudio/terminal.html'
visualisations_template_location = 'opstudio/visualisations.html'
settings_template_location = 'opstudio/settings.html'

DMP = dmp_module.diff_match_patch()
#DMP = diff_match_patch()
MAX_LEN_DIFF = 10

def match_row(db, lastcc, rowstr):
    res = {
        "start": lastcc,
        "end": lastcc
    }
    if not rowstr:
        return res
    simple_match_idx = db.find(rowstr, lastcc)
    if simple_match_idx != -1:
        return {"start": simple_match_idx, "end": simple_match_idx+len(rowstr)}
    start = match_right_context(db, lastcc, rowstr)
    while start != -1:
        res["start"] = start
        res["end"] = match_left_context(db, lastcc+len(rowstr), rowstr)
        if res["end"] != -1 and res["end"] > res["start"]:
            return res
        start = match_right_context(db, lastcc, rowstr)
    return None

# This might be better off somewhere else and could be know from
# the database
def detect_lang(s):
    c = ord(s[0])
    if c < 256:
        return "bo-x-ewts"
    elif c < 0x2E00 and c != 0x00B7:
        return "zh"
    else:
        return "zh"

def match_right_context(db, lastcc, rowstr):
    lang = detect_lang(rowstr)
    window_size = 20 if lang == "bo-x-ewts" else 5
    if window_size >= len(rowstr):
        window_size = len(rowstr)
    #print("trying to find \""+rowstr+"\" around \""+db[lastcc:lastcc+2*window_size])
    firstrowchars = rowstr[:window_size]
    simple_match = db.find(firstrowchars, lastcc)
    return DMP.match_main(db, rowstr, lastcc)

def match_left_context(db, expectedcc, rowstr):
    lang = detect_lang(rowstr)
    window_size = 20 if lang == "bo-x-ewts" else 5
    if window_size >= len(rowstr):
        window_size = len(rowstr)
    lastrowchars = rowstr[(len(rowstr)-window_size):]
    # we start a bit earlier so that we can get results in more cases
    simple_match = db.find(lastrowchars, expectedcc-2*window_size)
    # if not too far, return:
    if simple_match != -1 and abs(simple_match - expectedcc) < MAX_LEN_DIFF:
        return simple_match+window_size
    appmatch = DMP.match_main(db, lastrowchars, expectedcc-2*window_size)
    if appmatch == -1:
        return -1
    # then we have to reapply a simple match with a smaller window
    small_window_size = 5 if lang == "bo-x-ewts" else 1
    lastrowchars = rowstr[(len(rowstr)-small_window_size):]
    simple_match = db.find(lastrowchars, appmatch)
    if simple_match != -1:
        return simple_match+small_window_size
    # more approximate:
    return appmatch+window_size

def normalize_tib(s):
    s = re.sub(r"\[^[\]]+", "", s)
    s = s.replace("_", " ")
    s = s.replace("\n", "") # for csv
    return s.strip()

def normalize_zh(s):
    s = re.sub(r"\[^[\]]+", "", s)
    s = s.replace("\n", "") # for csv
    s = s.replace("，", "。") # normalize punctuation
    return s.strip()

def printmatch(db, rowstr, match):
    print("   initial in csv:")
    print("   "+rowstr)
    print("   found at characters "+str(match["start"])+":"+str(match["end"]))
    print("   "+db[match["start"]:match["end"]])

def grabcsv(csvlist, start, end):
    #cfile = request.FILES['csvfile']

    grabid = CsvAlignmentList.objects.filter(id=csvlist)[0].csvfile_id
    grabcsv = UserFile.objects.filter(id=grabid)[0]
    cfile = grabcsv.csvfile

    file_data = ""
    for chunk in cfile.chunks():
        file_data = file_data + str(chunk.decode("utf-8"))

    io_string = io.StringIO(file_data)
    #next(io_string)

    w1location = 0
    w2location = 0

    #start=50
    end=start+10

    #srcreader = csv.reader(io_string, delimiter=',', quotechar='"')
    #i, j = 50, 60
    #i, j = 0, 10
    #srcreader = csv.reader(itertools.islice(io_string, start, end+1), delimiter=',', quotechar='"')
    srcreader = csv.reader(io_string, delimiter=',', quotechar='"')
    fool = itertools.islice(srcreader, start, end+1)
    return fool

######

def index(request):
    error_msg = "error";
    template = loader.get_template(index_template_location)

    context = { }

    return HttpResponse(template.render(context, request))

@login_required
def ngrams(request):
    error_msg = "error";
    template = loader.get_template(ngrams_template_location)

    usersettings = UserSettings.objects.order_by('username_id')[0]
    current_user = request.user
    usersettings = UserSettings.objects.filter(username_id=current_user.id).order_by('username_id')[0]

    scrollvalue1 = "0"
    scrollvalue2 = "0"
    #scrollvalue_alignments = "0"

    latest_witness_list = Witness.objects.order_by('id').order_by('name')

    witness1 = latest_witness_list.filter(shortname="D45").first()
    witness2 = latest_witness_list.filter(shortname="T310_01").first()

    witness1_id = witness1.id
    witness2_id = witness2.id

    latest_partition_list1 = WitnessPartition.objects.filter(witness_id=witness1_id).order_by('char_start')
    latest_partition_list2 = WitnessPartition.objects.filter(witness_id=witness2_id).order_by('char_start')

    mrp1 = latest_partition_list1[0]
    mrp2 = latest_partition_list2[0]

    latest_annotations_list1 = Annotation.objects.filter(witness_id=witness1_id).order_by('char_start')
    latest_annotations_list2 = Annotation.objects.filter(witness_id=witness2_id).order_by('char_start')

    #latest_ngrams_list1 = NgramInWitness.objects.filter(witness_id=witness1_id).order_by('-frequency')[:nsize_filter]
    #latest_ngrams_list2 = NgramInWitness.objects.filter(witness_id=witness2_id).order_by('-frequency')[:nsize_filter]
    #latest_ngrams_list1 = NgramInWitness.objects.filter(witness_id=witness1_id).order_by('-nsize')[:nsize_filter]
    #latest_ngrams_list2 = NgramInWitness.objects.filter(witness_id=witness2_id).order_by('-nsize')[:nsize_filter]

    latest_ngrams_list1 = NgramInWitness.objects.filter(witness_id=witness1_id).order_by('-weight')[:nsize_filter]
    latest_ngrams_list2 = NgramInWitness.objects.filter(witness_id=witness2_id).order_by('-weight')[:nsize_filter]

    #latest_ngrams_list1 = NgramInWitness.objects.filter(witness_id=witness1_id).order_by('frequency')[:nsize_filter]
    #latest_ngrams_list2 = NgramInWitness.objects.filter(witness_id=witness2_id).order_by('frequency')[:nsize_filter]

    mrp1_id = mrp1.id
    mrp2_id = mrp2.id

    #latest_alignments_list = Alignment.objects.filter(witness_src_id=witness1_id).filter(witness_dst_id=witness2_id).order_by('char_start_src')
    #latest_alignments_list = Alignment.objects.filter(witness_src_id=mrp1.id).order_by('char_start_src')

    #latest_alignments_list = Alignment.objects.order_by('char_start_src')
    latest_alignments_list = Alignment.objects.filter(witness_src_id=witness1_id).filter(witness_dst_id=witness2_id).order_by('char_start_src')

    #latest_alignments_text = Alignment.objects.filter(witness_src_id=witness1_id).filter(witness_dst_id=witness2_id).order_by('char_start_src')
    #the corresponding text for each alignment, to be displayed in the lower window of manual selection screen

    partition_array =[]

    go_a1 = latest_partition_list1[0]

    if len(latest_partition_list1) > 2:
        go_b1 = latest_partition_list1[1]
        go_c1 = latest_partition_list1[2]
        new_p1 = go_a1.content + go_b1.content + go_c1.content
        last_char1 = go_c1.char_end

    elif len(latest_partition_list1) > 1:
        go_b1 = latest_partition_list1[1]
        new_p1 = go_a1.content + go_b1.content
        last_char1 = go_b1.char_end

    else:
        new_p1 = go_a1.content
        last_char1 = go_a1.char_end

    go_a2 = latest_partition_list2[0]

    if len(latest_partition_list2) > 2:
        go_b2 = latest_partition_list2[1]
        go_c2 = latest_partition_list2[2]
        new_p2 = go_a2.content + go_b2.content + go_c2.content
        last_char2 = go_c2.char_end

    elif len(latest_partition_list2) > 1:
        go_b2 = latest_partition_list2[1]
        new_p2 = go_a2.content + go_b2.content
        last_char2 = go_b2.char_end

    else:
        new_p2 = go_a2.content
        last_char2 = go_a2.char_end

    partition_array.append(new_p1)
    partition_array.append(new_p2)

    json_partition = json.dumps(partition_array)

    first_char1 = go_a1.char_start
    first_char2 = go_a2.char_start

    from1 = 0
    to1 = 0
    from2 = 0
    to2 = 0

    lastselection1_start = 0;
    lastselection1_end = 0;
    lastselection2_start = 0;
    lastselection2_end = 0;

    # if no other information given, then set base witness
    # for 1 and 2 to first available witness by ID

    if request.POST:
        post = request.POST.copy()
        reallypost = post['reallypost']
        clickstatus = post['clickstatus']

        scrollvalue1 = post['scrollvalue1']
        scrollvalue2 = post['scrollvalue2']
        #scrollvalue_alignments = post['scrollvalue_alignments']

        lastselection1_start = post['lastselection1_start'];        
        lastselection1_end = post['lastselection1_end'];
        lastselection2_start = post['lastselection2_start'];
        lastselection2_end = post['lastselection2_end'];

        try:
            segnum = post['provisionaldigit']
        except ValueError:
            segnum = ""

        try:
            seglet = post['provisionalletter']
        except ValueError:
            seglet = ""

        if segnum.isdigit():
            if seglet.isalpha():
                segname = segnum + "." + seglet
            else:
                segname = segnum
        else:
            segname = ""

        try:
            witness1_id = int(post['witness1_id'])
        except ValueError:
            witness1_id = latest_witness_list[0].id

        try:
            witness2_id = int(post['witness2_id'])
        except ValueError:
            witness2_id = latest_witness_list[0].id

        witness1 = latest_witness_list.get(id=witness1_id)
        witness2 = latest_witness_list.get(id=witness2_id)

        latest_partition_list1 = WitnessPartition.objects.filter(witness_id=witness1_id).order_by('char_start')
        latest_partition_list2 = WitnessPartition.objects.filter(witness_id=witness2_id).order_by('char_start')

        latest_alignments_list = Alignment.objects.filter(witness_src_id=witness1_id).filter(witness_dst_id=witness2_id).order_by('char_start_src')

        latest_annotations_list1 = Annotation.objects.filter(witness_id=witness1_id).order_by('char_start')
        latest_annotations_list2 = Annotation.objects.filter(witness_id=witness2_id).order_by('char_start')

        #latest_ngrams_list1 = NgramInWitness.objects.filter(witness_id=witness1_id).order_by('-frequency')[:nsize_filter]
        #latest_ngrams_list2 = NgramInWitness.objects.filter(witness_id=witness2_id).order_by('-frequency')[:nsize_filter]
        #latest_ngrams_list1 = NgramInWitness.objects.filter(witness_id=witness1_id).order_by('-nsize')[:nsize_filter]
        #latest_ngrams_list2 = NgramInWitness.objects.filter(witness_id=witness2_id).order_by('-nsize')[:nsize_filter]
        latest_ngrams_list1 = NgramInWitness.objects.filter(witness_id=witness1_id).order_by('-weight')[:nsize_filter]
        latest_ngrams_list2 = NgramInWitness.objects.filter(witness_id=witness2_id).order_by('-weight')[:nsize_filter]


        mrp1 = latest_partition_list1[0]
        mrp2 = latest_partition_list2[0]

        try:
            partition1_id = int(post['partition1_id'])
        except ValueError:
            partition1_id = mrp1.id
        try:
            partition2_id = int(post['partition2_id'])
        except ValueError:
            partition2_id = mrp2.id

        mrp1_id = partition1_id
        mrp2_id = partition2_id

        from1 = post['from1']
        try:
            from1 = int(post['from1'])
        except ValueError:
            from1 = None
        try:
            to1 = int(post['to1'])
        except ValueError:
            to1 = None
        try:
            from2 = int(post['from2'])
        except ValueError:
            from2 = None

        to2 = post['to2']
        try:
            to2 = int(post['to2'])
        except ValueError:
            to2 = None

        try:
            sc = int(post['score'])
        except ValueError:
            sc = None

        partition_array =[]

        try:
            go_a1 = latest_partition_list1.get(id=mrp1_id)
        except WitnessPartition.DoesNotExist:
            go_a1 = None

        if go_a1 != None:
            if (go_a1.witness_id != witness1_id):
                go_a1 = latest_partition_list1[0]
        
            if clickstatus== "w1left":
                try:
                    go_a1 = latest_partition_list1.get(char_end=go_a1.char_start)
                except WitnessPartition.DoesNotExist:
                    pass
                mrp1_id = go_a1.id
                
            elif clickstatus== "w1right":
                try:
                    go_a1 = latest_partition_list1.get(char_start=go_a1.char_end)
                except WitnessPartition.DoesNotExist:
                    pass
                mrp1_id = go_a1.id
                
        else:
            go_a1 = latest_partition_list1[0]
        
        first_char1 = go_a1.char_start
        go_b1_start = go_a1.char_end

        try:
            go_b1 = latest_partition_list1.get(char_start=go_b1_start)
        except WitnessPartition.DoesNotExist:
            go_b1 = None

        if go_b1 != None:
            go_c1_start = go_b1.char_end
            try:
                go_c1 = latest_partition_list1.get(char_start=go_c1_start)
            except WitnessPartition.DoesNotExist:
                go_c1 = None
            
            if go_c1 != None:
                new_p1 = go_a1.content + go_b1.content + go_c1.content
                last_char1 = go_c1.char_end
            else:
                new_p1 = go_a1.content + go_b1.content
                last_char1 = go_b1.char_end
        
        else:
            new_p1 = go_a1.content
            last_char1 = go_a1.char_end
            
        ################################################
        try:
            go_a2 = latest_partition_list2.get(id=mrp2_id)
        except WitnessPartition.DoesNotExist:
            go_a2 = None

        if go_a2 != None:
            if (go_a2.witness_id != witness2_id):
                go_a2 = latest_partition_list2[0]

            if clickstatus== "w2left":
                try:
                    go_a2 = latest_partition_list2.get(char_end=go_a2.char_start)
                except WitnessPartition.DoesNotExist:
                    pass
                mrp2_id = go_a2.id
                
            elif clickstatus== "w2right":
                try:
                    go_a2 = latest_partition_list2.get(char_start=go_a2.char_end)
                except WitnessPartition.DoesNotExist:
                    pass
                mrp2_id = go_a2.id
    
        else:
            go_a2 = latest_partition_list2[0]
            
        first_char2 = go_a2.char_start
        go_b2_start = go_a2.char_end

        try:
            go_b2 = latest_partition_list2.get(char_start=go_b2_start)
        except WitnessPartition.DoesNotExist:
            go_b2 = None

        if go_b2 != None:
            go_c2_start = go_b2.char_end
            try:
                go_c2 = latest_partition_list2.get(char_start=go_c2_start)
            except WitnessPartition.DoesNotExist:
                go_c2 = None
            
            if go_c2 != None:
                new_p2 = go_a2.content + go_b2.content + go_c2.content
                last_char2 = go_c2.char_end
            else:
                new_p2 = go_a2.content + go_b2.content
                last_char2 = go_b2.char_end
        
        else:
            new_p2 = go_a2.content
            last_char2 = go_a2.char_end
            
        ################################################
        ################################################
        
        partition_array.append(new_p1)
        partition_array.append(new_p2)

        # search partition array for dictionary matches
        #
        #

        mrp1 = latest_partition_list1.get(id=mrp1_id)
        mrp2 = latest_partition_list2.get(id=mrp2_id)

        json_partition = json.dumps(partition_array)

        if (from1 != None):
            cs_src=from1 + first_char1
        else:
            cs_src=from1

        if (to1 != None):
            ce_src=to1 + first_char1
        else:
            ce_src=to1

        if (from2 != None):
            cs_dst=from2 + first_char2
        else:
            cs_dst=from2

        if (to2 != None):
            ce_dst=to2 + first_char2
        else:
            ce_dst=to2

        t_id=2
        w_src_id=witness1_id
        w_dst_id=witness2_id

        segment_name = segname

        if(reallypost == "1"):
            alignment = Alignment.objects.create(witness_src_id=w_src_id, witness_dst_id=w_dst_id, char_start_src=cs_src, char_end_src=ce_src, char_start_dst=cs_dst, char_end_dst=ce_dst, score=sc, type_id=t_id, tentative_name=segment_name)
            alignment_log = AlignmentLog.objects.create(alignment_id=alignment.id, witness_src_id=w_src_id, witness_dst_id=w_dst_id, char_start_src=cs_src, char_end_src=ce_src, char_start_dst=cs_dst, char_end_dst=ce_dst, score=sc, type_id=t_id, user_id=current_user.id)
        # end create alignment, create log object
    
    context = {
    'latest_witness_list': latest_witness_list,
    'latest_alignments_list': latest_alignments_list,
    'latest_partition_list1': latest_partition_list1,
    'latest_partition_list2': latest_partition_list2,
    'latest_annotations_list1': latest_annotations_list1,
    'latest_annotations_list2': latest_annotations_list2,
    'latest_ngrams_list1': latest_ngrams_list1,
    'latest_ngrams_list2': latest_ngrams_list2,
    'most_recent_witness1': witness1,
    'most_recent_witness2': witness2,
    'most_recent_partition1': mrp1_id,
    'most_recent_partition2': mrp2_id,
    'partition_array': json_partition,
    'first_char1': first_char1,
    'last_char1': last_char1,
    'first_char2': first_char2,
    'last_char2': last_char2,
    'lastselection1_start': lastselection1_start,
    'lastselection1_end': lastselection1_end,
    'lastselection2_start': lastselection2_start,
    'lastselection2_end': lastselection2_end,
    'scrollvalue1': scrollvalue1,
    'scrollvalue2': scrollvalue2,
    #'scrollvalue_alignments': scrollvalue_alignments,
    #'usersettings': usersettings,
     }

    return HttpResponse(template.render(context, request))
@login_required
def alignments(request):
    error_msg = "error";
    template = loader.get_template(alignments_template_location)

    usersettings = UserSettings.objects.order_by('username_id')[0]
    current_user = request.user
    usersettings = UserSettings.objects.filter(username_id=current_user.id).order_by('username_id')[0]

    scrollvalue1 = "0"
    scrollvalue2 = "0"
    #scrollvalue_alignments = "0"

    latest_witness_list = Witness.objects.order_by('id').order_by('name')

    witness1 = latest_witness_list.filter(shortname="D45").first()
    witness2 = latest_witness_list.filter(shortname="T310_01").first()

    witness1_id = witness1.id
    witness2_id = witness2.id

    latest_partition_list1 = WitnessPartition.objects.filter(witness_id=witness1_id).order_by('char_start')
    latest_partition_list2 = WitnessPartition.objects.filter(witness_id=witness2_id).order_by('char_start')

    mrp1 = latest_partition_list1[0]
    mrp2 = latest_partition_list2[0]

    latest_annotations_list1 = Annotation.objects.filter(witness_id=witness1_id).order_by('char_start')
    latest_annotations_list2 = Annotation.objects.filter(witness_id=witness2_id).order_by('char_start')

    #latest_ngrams_list1 = NgramInWitness.objects.filter(witness_id=witness1_id).order_by('-frequency')[:nsize_filter]
    #latest_ngrams_list2 = NgramInWitness.objects.filter(witness_id=witness2_id).order_by('-frequency')[:nsize_filter]
    #latest_ngrams_list1 = NgramInWitness.objects.filter(witness_id=witness1_id).order_by('-nsize')[:nsize_filter]
    #latest_ngrams_list2 = NgramInWitness.objects.filter(witness_id=witness2_id).order_by('-nsize')[:nsize_filter]
    latest_ngrams_list1 = NgramInWitness.objects.filter(witness_id=witness1_id).order_by('-weight')[:nsize_filter]
    latest_ngrams_list2 = NgramInWitness.objects.filter(witness_id=witness2_id).order_by('-weight')[:nsize_filter]

    mrp1_id = mrp1.id
    mrp2_id = mrp2.id

    #latest_alignments_list = Alignment.objects.filter(witness_src_id=witness1_id).filter(witness_dst_id=witness2_id).order_by('char_start_src')
    #latest_alignments_list = Alignment.objects.filter(witness_src_id=mrp1.id).order_by('char_start_src')

    #latest_alignments_list = Alignment.objects.order_by('char_start_src')
    latest_alignments_list = Alignment.objects.filter(witness_src_id=witness1_id).filter(witness_dst_id=witness2_id).order_by('char_start_src')

    #latest_alignments_text = Alignment.objects.filter(witness_src_id=witness1_id).filter(witness_dst_id=witness2_id).order_by('char_start_src')
    #the corresponding text for each alignment, to be displayed in the lower window of manual selection screen

    partition_array =[]

    go_a1 = latest_partition_list1[0]

    if len(latest_partition_list1) > 2:
        go_b1 = latest_partition_list1[1]
        go_c1 = latest_partition_list1[2]
        new_p1 = go_a1.content + go_b1.content + go_c1.content
        last_char1 = go_c1.char_end

    elif len(latest_partition_list1) > 1:
        go_b1 = latest_partition_list1[1]
        new_p1 = go_a1.content + go_b1.content
        last_char1 = go_b1.char_end

    else:
        new_p1 = go_a1.content
        last_char1 = go_a1.char_end

    go_a2 = latest_partition_list2[0]

    if len(latest_partition_list2) > 2:
        go_b2 = latest_partition_list2[1]
        go_c2 = latest_partition_list2[2]
        new_p2 = go_a2.content + go_b2.content + go_c2.content
        last_char2 = go_c2.char_end

    elif len(latest_partition_list2) > 1:
        go_b2 = latest_partition_list2[1]
        new_p2 = go_a2.content + go_b2.content
        last_char2 = go_b2.char_end

    else:
        new_p2 = go_a2.content
        last_char2 = go_a2.char_end

    partition_array.append(new_p1)
    partition_array.append(new_p2)

    json_partition = json.dumps(partition_array)

    first_char1 = go_a1.char_start
    first_char2 = go_a2.char_start

    from1 = 0
    to1 = 0
    from2 = 0
    to2 = 0

    lastselection1_start = 0;
    lastselection1_end = 0;
    lastselection2_start = 0;
    lastselection2_end = 0;

    # if no other information given, then set base witness
    # for 1 and 2 to first available witness by ID

    if request.POST:
        post = request.POST.copy()
        reallypost = post['reallypost']
        clickstatus = post['clickstatus']

        scrollvalue1 = post['scrollvalue1']
        scrollvalue2 = post['scrollvalue2']
        #scrollvalue_alignments = post['scrollvalue_alignments']

        lastselection1_start = post['lastselection1_start'];        
        lastselection1_end = post['lastselection1_end'];
        lastselection2_start = post['lastselection2_start'];
        lastselection2_end = post['lastselection2_end'];

        try:
            segnum = post['provisionaldigit']
        except ValueError:
            segnum = ""

        try:
            seglet = post['provisionalletter']
        except ValueError:
            seglet = ""

        if segnum.isdigit():
            if seglet.isalpha():
                segname = segnum + "." + seglet
            else:
                segname = segnum
        else:
            segname = ""

        try:
            witness1_id = int(post['witness1_id'])
        except ValueError:
            witness1_id = latest_witness_list[0].id

        try:
            witness2_id = int(post['witness2_id'])
        except ValueError:
            witness2_id = latest_witness_list[0].id

        witness1 = latest_witness_list.get(id=witness1_id)
        witness2 = latest_witness_list.get(id=witness2_id)

        latest_partition_list1 = WitnessPartition.objects.filter(witness_id=witness1_id).order_by('char_start')
        latest_partition_list2 = WitnessPartition.objects.filter(witness_id=witness2_id).order_by('char_start')

        latest_alignments_list = Alignment.objects.filter(witness_src_id=witness1_id).filter(witness_dst_id=witness2_id).order_by('char_start_src')

        latest_annotations_list1 = Annotation.objects.filter(witness_id=witness1_id).order_by('char_start')
        latest_annotations_list2 = Annotation.objects.filter(witness_id=witness2_id).order_by('char_start')

        latest_ngrams_list1 = NgramInWitness.objects.filter(witness_id=witness1_id).order_by('-frequency')[:nsize_filter]
        latest_ngrams_list2 = NgramInWitness.objects.filter(witness_id=witness2_id).order_by('-frequency')[:nsize_filter]
        #latest_ngrams_list1 = NgramInWitness.objects.filter(witness_id=witness1_id).order_by('-nsize')[:nsize_filter]
        #latest_ngrams_list2 = NgramInWitness.objects.filter(witness_id=witness2_id).order_by('-nsize')[:nsize_filter]
        #latest_ngrams_list1 = NgramInWitness.objects.filter(witness_id=witness1_id).order_by('frequency')[:nsize_filter]
        #latest_ngrams_list2 = NgramInWitness.objects.filter(witness_id=witness2_id).order_by('frequency')[:nsize_filter]


        mrp1 = latest_partition_list1[0]
        mrp2 = latest_partition_list2[0]

        try:
            partition1_id = int(post['partition1_id'])
        except ValueError:
            partition1_id = mrp1.id
        try:
            partition2_id = int(post['partition2_id'])
        except ValueError:
            partition2_id = mrp2.id

        mrp1_id = partition1_id
        mrp2_id = partition2_id

        from1 = post['from1']
        try:
            from1 = int(post['from1'])
        except ValueError:
            from1 = None
        try:
            to1 = int(post['to1'])
        except ValueError:
            to1 = None
        try:
            from2 = int(post['from2'])
        except ValueError:
            from2 = None

        to2 = post['to2']
        try:
            to2 = int(post['to2'])
        except ValueError:
            to2 = None

        try:
            sc = int(post['score'])
        except ValueError:
            sc = None

        partition_array =[]

        try:
            go_a1 = latest_partition_list1.get(id=mrp1_id)
        except WitnessPartition.DoesNotExist:
            go_a1 = None

        if go_a1 != None:
            if (go_a1.witness_id != witness1_id):
                go_a1 = latest_partition_list1[0]
        
            if clickstatus== "w1left":
                try:
                    go_a1 = latest_partition_list1.get(char_end=go_a1.char_start)
                except WitnessPartition.DoesNotExist:
                    pass
                mrp1_id = go_a1.id
                
            elif clickstatus== "w1right":
                try:
                    go_a1 = latest_partition_list1.get(char_start=go_a1.char_end)
                except WitnessPartition.DoesNotExist:
                    pass
                mrp1_id = go_a1.id
                
        else:
            go_a1 = latest_partition_list1[0]
        
        first_char1 = go_a1.char_start
        go_b1_start = go_a1.char_end

        try:
            go_b1 = latest_partition_list1.get(char_start=go_b1_start)
        except WitnessPartition.DoesNotExist:
            go_b1 = None

        if go_b1 != None:
            go_c1_start = go_b1.char_end
            try:
                go_c1 = latest_partition_list1.get(char_start=go_c1_start)
            except WitnessPartition.DoesNotExist:
                go_c1 = None
            
            if go_c1 != None:
                new_p1 = go_a1.content + go_b1.content + go_c1.content
                last_char1 = go_c1.char_end
            else:
                new_p1 = go_a1.content + go_b1.content
                last_char1 = go_b1.char_end
        
        else:
            new_p1 = go_a1.content
            last_char1 = go_a1.char_end
            
        ################################################
        try:
            go_a2 = latest_partition_list2.get(id=mrp2_id)
        except WitnessPartition.DoesNotExist:
            go_a2 = None

        if go_a2 != None:
            if (go_a2.witness_id != witness2_id):
                go_a2 = latest_partition_list2[0]

            if clickstatus== "w2left":
                try:
                    go_a2 = latest_partition_list2.get(char_end=go_a2.char_start)
                except WitnessPartition.DoesNotExist:
                    pass
                mrp2_id = go_a2.id
                
            elif clickstatus== "w2right":
                try:
                    go_a2 = latest_partition_list2.get(char_start=go_a2.char_end)
                except WitnessPartition.DoesNotExist:
                    pass
                mrp2_id = go_a2.id
    
        else:
            go_a2 = latest_partition_list2[0]
            
        first_char2 = go_a2.char_start
        go_b2_start = go_a2.char_end

        try:
            go_b2 = latest_partition_list2.get(char_start=go_b2_start)
        except WitnessPartition.DoesNotExist:
            go_b2 = None

        if go_b2 != None:
            go_c2_start = go_b2.char_end
            try:
                go_c2 = latest_partition_list2.get(char_start=go_c2_start)
            except WitnessPartition.DoesNotExist:
                go_c2 = None
            
            if go_c2 != None:
                new_p2 = go_a2.content + go_b2.content + go_c2.content
                last_char2 = go_c2.char_end
            else:
                new_p2 = go_a2.content + go_b2.content
                last_char2 = go_b2.char_end
        
        else:
            new_p2 = go_a2.content
            last_char2 = go_a2.char_end
            
        ################################################
        ################################################
        
        partition_array.append(new_p1)
        partition_array.append(new_p2)

        # search partition array for dictionary matches
        #
        #

        mrp1 = latest_partition_list1.get(id=mrp1_id)
        mrp2 = latest_partition_list2.get(id=mrp2_id)

        json_partition = json.dumps(partition_array)

        if (from1 != None):
            cs_src=from1 + first_char1
        else:
            cs_src=from1

        if (to1 != None):
            ce_src=to1 + first_char1
        else:
            ce_src=to1

        if (from2 != None):
            cs_dst=from2 + first_char2
        else:
            cs_dst=from2

        if (to2 != None):
            ce_dst=to2 + first_char2
        else:
            ce_dst=to2

        t_id=2
        w_src_id=witness1_id
        w_dst_id=witness2_id

        segment_name = segname

        if(reallypost == "1"):
            alignment = Alignment.objects.create(witness_src_id=w_src_id, witness_dst_id=w_dst_id, char_start_src=cs_src, char_end_src=ce_src, char_start_dst=cs_dst, char_end_dst=ce_dst, score=sc, type_id=t_id, tentative_name=segment_name)
            alignment_log = AlignmentLog.objects.create(alignment_id=alignment.id, witness_src_id=w_src_id, witness_dst_id=w_dst_id, char_start_src=cs_src, char_end_src=ce_src, char_start_dst=cs_dst, char_end_dst=ce_dst, score=sc, type_id=t_id, user_id=current_user.id)
        # end create alignment, create log object
    
    context = {
    'latest_witness_list': latest_witness_list,
    'latest_alignments_list': latest_alignments_list,
    'latest_partition_list1': latest_partition_list1,
    'latest_partition_list2': latest_partition_list2,
    'latest_annotations_list1': latest_annotations_list1,
    'latest_annotations_list2': latest_annotations_list2,
    'latest_ngrams_list1': latest_ngrams_list1,
    'latest_ngrams_list2': latest_ngrams_list2,
    'most_recent_witness1': witness1,
    'most_recent_witness2': witness2,
    'most_recent_partition1': mrp1_id,
    'most_recent_partition2': mrp2_id,
    'partition_array': json_partition,
    'first_char1': first_char1,
    'last_char1': last_char1,
    'first_char2': first_char2,
    'last_char2': last_char2,
    'lastselection1_start': lastselection1_start,
    'lastselection1_end': lastselection1_end,
    'lastselection2_start': lastselection2_start,
    'lastselection2_end': lastselection2_end,
    'scrollvalue1': scrollvalue1,
    'scrollvalue2': scrollvalue2,
    #'scrollvalue_alignments': scrollvalue_alignments,
    #'usersettings': usersettings,
     }

    return HttpResponse(template.render(context, request))

#@login_required
def upload(request):
    error_msg = "error";
    template = loader.get_template(upload_template_location)

    # Handle file upload
    w1content = ""
    w2content = ""
    alignments = []
    matches = []
    i, j = 0, 10

    w1partitions = []
    w2partitions = []

    #matchstatus = 0

    if request.method == 'POST':
        #witness_list = Witness.objects.order_by('id')

        post = request.POST.copy()
        witness_src = post['witness_src']
        witness_dst = post['witness_dst']

        witness1 = Witness.objects.filter(id=witness_src).order_by('id')[0]
        witness2 = Witness.objects.filter(id=witness_dst).order_by('id')[0]

        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            newcsv = UserFile(csvfile = request.FILES['csvfile'], witness_src = witness1, witness_dst = witness2)
            newcsv.save()

            #grabid = newcsv.id

            csvlist = CsvAlignmentList(name="nothing", csvfile_id=newcsv.id)
            csvlist.save()
            csv_id = csvlist.id
            #grabid = csvlist.csvfile_id

            w1partitions = WitnessPartition.objects.filter(witness_id=witness_src).order_by('char_start')
            w2partitions = WitnessPartition.objects.filter(witness_id=witness_dst).order_by('char_start')

            w1content = ""
            for partition in w1partitions:
                w1content = w1content + partition.content

            w2content = ""
            for partition in w2partitions:
                w2content = w2content + partition.content

            alignments = Alignment.objects.filter(witness_src_id=witness_src)

            """
            #cfile = request.FILES['csvfile']
            grabcsv = UserFile.objects.filter(id=grabid)[0]
            cfile = grabcsv.csvfile

            file_data = ""
            for chunk in cfile.chunks():
                file_data = file_data + str(chunk.decode("utf-8"))

            io_string = io.StringIO(file_data)
            #next(io_string)
            """

            w1location = 0
            w2location = 0

            #srcreader = csv.reader(io_string, delimiter=',', quotechar='"')
            #i, j = 50, 60
            #i, j = 0, 10
            #srcreader = csv.reader(itertools.islice(io_string, i, j+1), delimiter=',', quotechar='"')
            #srcreader = grabcsv(grabid, csv_id, start, end)
            #srcreader = grabcsv(grabid, csv_id, i, j)
            srcreader = grabcsv(csv_id, i, j)

            dbtib = w1content
            dbtib = normalize_tib(dbtib)

            dbzh = w2content
            dbzh = normalize_zh(dbzh)

            tiblastcc = 0
            zhlastcc = 0

            # elie's code
            for row in srcreader:
                csvtib = normalize_tib(row[0])
                csvzh = normalize_zh(row[1]).replace(" ", "") # quite important to replace the spaces only in the csv
                if len(row) > 2:
                    matchscore = row[2]
                else:
                    matchscore = 0

                matchtib = match_row(dbtib, tiblastcc, csvtib)
                matchzh = match_row(dbzh, zhlastcc, csvzh)

                if matchtib:
                    tiblastcc = matchtib["end"]
                    w1match = matchtib["start"]
                    w1matchend = matchtib["end"]

                    w1matchlength = len(csvtib)
                    w1matchtarget = csvtib
                    w1matchfound = dbtib[w1match:w1matchend]
                else:
                    w1match = -1

                if matchzh:
                    zhlastcc = matchzh["end"]
                    w2match = matchzh["start"]
                    w2matchend = matchzh["end"]

                    w2matchlength = len(csvzh)
                    w2matchtarget = csvzh
                    w2matchfound = dbzh[w2match:w2matchend]
                else:
                    w2match = -1

                    #witness_src_id=witness_src, witness_dst_id=witness_dst, char_start_src=this1match, char_end_src=this1end, char_start_dst=this2match, char_end_dst=this2end, score=0, type_id=2, tentative_name="csv_addition"

                #matchstatus = 0
                if matchtib and matchzh:
                    #if Alignment.objects.filter(witness_src_id=witness_src, witness_dst_id=witness_dst, char_start_src=w1match, char_end_src=w1matchend).exists():
                    if Alignment.objects.filter(witness_src_id=witness_src, witness_dst_id=witness_dst, char_start_src=w1match, char_start_dst=w2match).exists():
                    #if Alignment.objects.filter(witness_src_id=witness_src, witness_dst_id=witness_dst).exists():
                    #if Alignment.objects.filter(witness_src_id=witness_src, witness_dst_id=witness_dst, char_start_src=w1match, char_end_src=w1matchend, char_start_dst=w2match, char_end_dst=w2matchend).exists():
                    #if Alignment.objects.filter(witness_src_id=witness_src, witness_dst_id=witness_dst, char_start_src=w1match, char_start_dst=w2match).exists():
                        kludge = 1
                        matchstatus = 1

                    matches.append((w1match, w1matchlength, w1matchtarget, w1matchfound, w2match, w2matchlength, w2matchtarget, w2matchfound, matchscore, matchstatus))

                    # add this alignment to the list so we can grab it back
                    csvalign = CsvAlignment(csvlist=csvlist, w1match=w1match, w1matchlength=w1matchlength, w1matchtarget=w1matchtarget, w1matchfound=w1matchfound, w2match=w2match, w2matchlength=w2matchlength, w2matchtarget=w2matchtarget, w2matchfound=w2matchfound, score=matchscore)
                    csvalign.save()
            #"""
    else:
        form = UploadForm() # A empty, unbound form
        csv_id = -1
        witness_src = -1
        witness_dst = -1

    # Load documents for the list page
    #documents = UserFile.objects.all()

    #witnesses = Witness.objects.all()
    #alignments = Alignment.objects.all()

    # Render list page with the documents and the form
    context = {
    'csv_id': csv_id,
    'witness_src': witness_src,
    'witness_dst': witness_dst,
    #'witnesses': witnesses,
    #'w1content': w1content,
    #'w2content': w2content,
    #'w1partitions': w1partitions,
    #'w2partitions': w2partitions,
    #'alignments': alignments,
    'form': form,
    'matches': matches,
    'csv_startpoint': i,
    'csv_endpoint': j,
    }
    return render(request, upload_template_location, context)


    #text1 = request.POST.get('text1')
    #    text2 = request.POST.get('text2')
    #
    #    if request.POST.get("d1"):
    #        dict1 = "on"
    #    else:
    #        dict1 = "off"


    context = { }

    return HttpResponse(template.render(context, request))

#@login_required
def search(request):
    template = search_template
    if request.POST:
        term1 = request.POST.get('term1')
        d = DictionaryEntry.objects.filter(entry1=term1) | DictionaryEntry.objects.filter(entry2=term1)

        context = { "matches" : d, }
        return render(request, template, context)
    return render(request,template,{})


@login_required
def importer(request):
    # Handle file upload
    w1content = ""
    w2content = ""
    alignments = []
    matches = []
    i, j = 0, 10

    w1partitions = []
    w2partitions = []

    if request.method == 'POST':
        matchstatus = 0
        #witness_list = Witness.objects.order_by('id')

        post = request.POST.copy()
        witness_src = post['witness_src']
        witness_dst = post['witness_dst']

        witness1 = Witness.objects.filter(id=witness_src).order_by('id')[0]
        witness2 = Witness.objects.filter(id=witness_dst).order_by('id')[0]

        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            newcsv = UserFile(csvfile = request.FILES['csvfile'], witness_src = witness1, witness_dst = witness2)
            newcsv.save()

            #grabid = newcsv.id

            csvlist = CsvAlignmentList(name="nothing", csvfile_id=newcsv.id)
            csvlist.save()
            csv_id = csvlist.id
            #grabid = csvlist.csvfile_id

            w1partitions = WitnessPartition.objects.filter(witness_id=witness_src).order_by('char_start')
            w2partitions = WitnessPartition.objects.filter(witness_id=witness_dst).order_by('char_start')

            w1content = ""
            for partition in w1partitions:
                w1content = w1content + partition.content

            w2content = ""
            for partition in w2partitions:
                w2content = w2content + partition.content

            alignments = Alignment.objects.filter(witness_src_id=witness_src)

            """
            #cfile = request.FILES['csvfile']
            grabcsv = UserFile.objects.filter(id=grabid)[0]
            cfile = grabcsv.csvfile

            file_data = ""
            for chunk in cfile.chunks():
                file_data = file_data + str(chunk.decode("utf-8"))

            io_string = io.StringIO(file_data)
            #next(io_string)
            """

            w1location = 0
            w2location = 0

            #srcreader = csv.reader(io_string, delimiter=',', quotechar='"')
            #i, j = 50, 60
            #i, j = 0, 10
            #srcreader = csv.reader(itertools.islice(io_string, i, j+1), delimiter=',', quotechar='"')
            #srcreader = grabcsv(grabid, csv_id, start, end)
            #srcreader = grabcsv(grabid, csv_id, i, j)
            srcreader = grabcsv(csv_id, i, j)

            dbtib = w1content
            dbtib = normalize_tib(dbtib)

            dbzh = w2content
            dbzh = normalize_zh(dbzh)

            tiblastcc = 0
            zhlastcc = 0

            # elie's code
            for row in srcreader:
                csvtib = normalize_tib(row[0])
                csvzh = normalize_zh(row[1]).replace(" ", "") # quite important to replace the spaces only in the csv
                if len(row) > 2:
                    matchscore = row[2]
                else:
                    matchscore = 0

                matchtib = match_row(dbtib, tiblastcc, csvtib)
                matchzh = match_row(dbzh, zhlastcc, csvzh)

                if matchtib:
                    tiblastcc = matchtib["end"]
                    w1match = matchtib["start"]
                    w1matchend = matchtib["end"]

                    w1matchlength = len(csvtib)
                    w1matchtarget = csvtib
                    w1matchfound = dbtib[w1match:w1matchend]
                else:
                    w1match = -1

                if matchzh:
                    zhlastcc = matchzh["end"]
                    w2match = matchzh["start"]
                    w2matchend = matchzh["end"]

                    w2matchlength = len(csvzh)
                    w2matchtarget = csvzh
                    w2matchfound = dbzh[w2match:w2matchend]
                else:
                    w2match = -1

                    #witness_src_id=witness_src, witness_dst_id=witness_dst, char_start_src=this1match, char_end_src=this1end, char_start_dst=this2match, char_end_dst=this2end, score=0, type_id=2, tentative_name="csv_addition"

                #matchstatus = 0
                if matchtib and matchzh:
                    matchstatus = 0
                    #if Alignment.objects.filter(witness_src_id=witness_src, witness_dst_id=witness_dst, char_start_src=w1match, char_end_src=w1matchend, char_start_dst=w2match, char_end_dst=w2matchend).exists():
                    #if Alignment.objects.filter(witness_src_id=witness_src, witness_dst_id=witness_dst, char_start_src=w1match, char_start_dst=w2match).exists():
                    if Alignment.objects.filter(witness_src_id=witness_src, witness_dst_id=witness_dst, char_start_src=w1match, char_start_dst=w2match).exists():
                    #if Alignment.objects.filter(witness_src_id=witness_src, witness_dst_id=witness_dst).exists():

                        #kludge = 1
                        matchstatus = 1

                    matches.append((w1match, w1matchlength, w1matchtarget, w1matchfound, w2match, w2matchlength, w2matchtarget, w2matchfound, matchscore, matchstatus))

                    # add this alignment to the list so we can grab it back
                    csvalign = CsvAlignment(csvlist=csvlist, w1match=w1match, w1matchlength=w1matchlength, w1matchtarget=w1matchtarget, w1matchfound=w1matchfound, w2match=w2match, w2matchlength=w2matchlength, w2matchtarget=w2matchtarget, w2matchfound=w2matchfound, score=matchscore)
                    csvalign.save()
    else:
        form = UploadForm() # A empty, unbound form
        csv_id = -1
        witness_src = -1
        witness_dst = -1

    # Load documents for the list page
    #documents = UserFile.objects.all()

    #witnesses = Witness.objects.all()
    #alignments = Alignment.objects.all()

    # Render list page with the documents and the form
    context = {
    'csv_id': csv_id,
    'witness_src': witness_src,
    'witness_dst': witness_dst,
    #'witnesses': witnesses,
    #'w1content': w1content,
    #'w2content': w2content,
    #'w1partitions': w1partitions,
    #'w2partitions': w2partitions,
    #'alignments': alignments,
    'form': form,
    'matches': matches,
    'csv_startpoint': i,
    'csv_endpoint': j,
    }
    return render(request, importer_template_location, context)

@login_required
def add_alignment(request):
    # Handle file upload
    w1content = ""
    w2content = ""
    alignments = []
    matches = []

    w1partitions = []
    w2partitions = []

    if request.method == 'POST':
        #witness_list = Witness.objects.order_by('id')

        post = request.POST.copy()
        witness_src = post['witness_src']
        witness_dst = post['witness_dst']
        csv_id = post['csv_id']

        witness1 = Witness.objects.filter(id=witness_src).order_by('id')[0]
        witness2 = Witness.objects.filter(id=witness_dst).order_by('id')[0]

        this1match = post['this1match']
        this1matchlength = post['this1matchlength']
        #this1matchtarget = post['this1matchtarget']
        #this1matchfound = post['this1matchfound']
        this2match = post['this2match']
        this2matchlength = post['this2matchlength']
        #this2matchtarget = post['this2matchtarget']
        #this2matchfound = post['this2matchfound']

        this1end = int(this1match) + int(this1matchlength)
        this2end = int(this2match) + int(this2matchlength)

        #i = int(post['csv_startpoint'])
        #j = int(post['csv_endpoint'])

        startpoint = int(post['csv_startpoint'])
        endpoint = int(post['csv_endpoint'])
        score = int(post['score'])
        #score = 11

        #if startpoint < 0:
        #    startpoint = 0
        endpoint = startpoint + 10

        #
        w1partitions = WitnessPartition.objects.filter(witness_id=witness_src).order_by('char_start')
        w2partitions = WitnessPartition.objects.filter(witness_id=witness_dst).order_by('char_start')

        w1content = ""
        for partition in w1partitions:
            w1content = w1content + partition.content

        w2content = ""
        for partition in w2partitions:
            w2content = w2content + partition.content

        #alignments = Alignment.objects.filter(witness_src_id=witness_src)
        #

        alignment = Alignment.objects.create(witness_src_id=witness_src, witness_dst_id=witness_dst, char_start_src=this1match, char_end_src=this1end, char_start_dst=this2match, char_end_dst=this2end, score=score, type_id=2, tentative_name="csv_addition")        
        #alignment.save()

        # elie
        #i, j = 0, 10
        #srcreader = csv.reader(itertools.islice(io_string, i, j+1), delimiter=',', quotechar='"')
        #srcreader = grabcsv(grabid, csv_id, start, end)
        #srcreader = grabcsv(grabid, csv_id, i, j)
        srcreader = grabcsv(csv_id, startpoint, endpoint)

        dbtib = w1content
        dbtib = normalize_tib(dbtib)

        dbzh = w2content
        dbzh = normalize_zh(dbzh)

        tiblastcc = 0
        zhlastcc = 0

        # elie's code
        for row in srcreader:
            csvtib = normalize_tib(row[0])
            csvzh = normalize_zh(row[1]).replace(" ", "") # quite important to replace the spaces only in the csv
            if len(row) > 2:
                matchscore = row[2]
            else:
                matchscore = 0

            matchtib = match_row(dbtib, tiblastcc, csvtib)
            matchzh = match_row(dbzh, zhlastcc, csvzh)

            if matchtib:
                tiblastcc = matchtib["end"]
                w1match = matchtib["start"]
                w1matchend = matchtib["end"]

                w1matchlength = len(csvtib)
                w1matchtarget = csvtib
                w1matchfound = dbtib[w1match:w1matchend]
            else:
                w1match = -1

            if matchzh:
                zhlastcc = matchzh["end"]
                w2match = matchzh["start"]
                w2matchend = matchzh["end"]

                w2matchlength = len(csvzh)
                w2matchtarget = csvzh
                w2matchfound = dbzh[w2match:w2matchend]
            else:
                w2match = -1

                #witness_src_id=witness_src, witness_dst_id=witness_dst, char_start_src=this1match, char_end_src=this1end, char_start_dst=this2match, char_end_dst=this2end, score=0, type_id=2, tentative_name="csv_addition"

            #matchstatus = 0
            if matchtib and matchzh:
                #matchscore = 0
                matchstatus = 0
                #if Alignment.objects.filter(witness_src_id=witness_src, witness_dst_id=witness_dst, char_start_src=w1match, char_end_src=w1matchend).exists():
                if Alignment.objects.filter(witness_src_id=witness_src, witness_dst_id=witness_dst, char_start_src=w1match, char_start_dst=w2match).exists():
                #if Alignment.objects.filter(witness_src_id=witness_src, witness_dst_id=witness_dst).exists():
                    #kludge = 1
                    matchstatus = 1

                matches.append((w1match, w1matchlength, w1matchtarget, w1matchfound, w2match, w2matchlength, w2matchtarget, w2matchfound, matchscore, matchstatus))

                # add this alignment to the list so we can grab it back
                #csvalign = CsvAlignment(csvlist=csvlist, w1match=w1match, w1matchlength=w1matchlength, w1matchtarget=w1matchtarget, w1matchfound=w1matchfound, w2match=w2match, w2matchlength=w2matchlength, w2matchtarget=w2matchtarget, w2matchfound=w2matchfound)
                #csvalign.save()
        # elie

    # Load documents for the list page
    #documents = UserFile.objects.all()
    witnesses = Witness.objects.all()
    #alignments = Alignment.objects.all()

    # Render list page with the documents and the form
    context = {
    'csv_id': csv_id,
    'witness_src': witness_src,
    'witness_dst': witness_dst,
    'witnesses': witnesses,
    'w1content': w1content,
    'w2content': w2content,
    'w1partitions': w1partitions,
    'w2partitions': w2partitions,
    'alignments': alignments,
    #'form': form,
    'matches': matches,
    'csv_startpoint': startpoint,
    'csv_endpoint': endpoint,
    }
    return render(request, importer_template_location, context)

#@login_required
def navalign(request):
    # Handle file upload
    w1content = ""
    w2content = ""
    alignments = []
    matches = []

    w1partitions = []
    w2partitions = []

    if request.method == 'POST':
        #witness_list = Witness.objects.order_by('id')

        post = request.POST.copy()
        witness_src = post['witness_src']
        witness_dst = post['witness_dst']
        csv_id = post['csv_id']

        witness1 = Witness.objects.filter(id=witness_src).order_by('id')[0]
        witness2 = Witness.objects.filter(id=witness_dst).order_by('id')[0]

        this1match = post['this1match']
        this1matchlength = post['this1matchlength']
        #this1matchtarget = post['this1matchtarget']
        #this1matchfound = post['this1matchfound']
        this2match = post['this2match']
        this2matchlength = post['this2matchlength']

        #startpoint = int(post['csv_startpoint'])
        #endpoint = int(post['csv_endpoint'])

        #if startpoint < 0:
        #    startpoint = 0
        #endpoint = startpoint + 10

        startpoint = int(post['csv_startpoint'])
        endpoint = int(post['csv_endpoint'])

        #if startpoint < 0:
        #    startpoint = 0
        endpoint = startpoint + 10

        #this2matchtarget = post['this2matchtarget']
        #this2matchfound = post['this2matchfound']

        #this1end = int(this1match) + int(this1matchlength)
        #this2end = int(this2match) + int(this2matchlength)

        #alignment = Alignment.objects.create(witness_src_id=witness_src, witness_dst_id=witness_dst, char_start_src=this1match, char_end_src=this1end, char_start_dst=this2match, char_end_dst=this2end, score=0, type_id=2, tentative_name="csv_addition")        
        #alignment.save()

                # elie

        w1partitions = WitnessPartition.objects.filter(witness_id=witness_src).order_by('char_start')
        w2partitions = WitnessPartition.objects.filter(witness_id=witness_dst).order_by('char_start')

        w1content = ""
        for partition in w1partitions:
            w1content = w1content + partition.content

        w2content = ""
        for partition in w2partitions:
            w2content = w2content + partition.content

        alignments = Alignment.objects.filter(witness_src_id=witness_src)

        """
        #cfile = request.FILES['csvfile']
        grabcsv = UserFile.objects.filter(id=grabid)[0]
        cfile = grabcsv.csvfile

        file_data = ""
        for chunk in cfile.chunks():
            file_data = file_data + str(chunk.decode("utf-8"))

        io_string = io.StringIO(file_data)
        #next(io_string)
        """

        w1location = 0
        w2location = 0


        #i, j = 10, 20
        #srcreader = csv.reader(itertools.islice(io_string, i, j+1), delimiter=',', quotechar='"')
        #srcreader = grabcsv(grabid, csv_id, start, end)
        #srcreader = grabcsv(grabid, csv_id, i, j)
        #srcreader = grabcsv(csv_id, i, j)
        #srcreader = grabcsv(220,0,0)
        srcreader = grabcsv(csv_id,startpoint,endpoint)

        dbtib = w1content
        dbtib = normalize_tib(dbtib)

        dbzh = w2content
        dbzh = normalize_zh(dbzh)

        tiblastcc = 0
        zhlastcc = 0

        # elie's code
        for row in srcreader:
            csvtib = normalize_tib(row[0])
            csvzh = normalize_zh(row[1]).replace(" ", "") # quite important to replace the spaces only in the csv
            if len(row) > 2:
                matchscore = row[2]
            else:
                matchscore = 0

            matchtib = match_row(dbtib, tiblastcc, csvtib)
            matchzh = match_row(dbzh, zhlastcc, csvzh)

            if matchtib:
                tiblastcc = matchtib["end"]
                w1match = matchtib["start"]
                w1matchend = matchtib["end"]

                w1matchlength = len(csvtib)
                w1matchtarget = csvtib
                w1matchfound = dbtib[w1match:w1matchend]
            else:
                w1match = -1

            if matchzh:
                zhlastcc = matchzh["end"]
                w2match = matchzh["start"]
                w2matchend = matchzh["end"]

                w2matchlength = len(csvzh)
                w2matchtarget = csvzh
                w2matchfound = dbzh[w2match:w2matchend]
            else:
                w2match = -1

                #witness_src_id=witness_src, witness_dst_id=witness_dst, char_start_src=this1match, char_end_src=this1end, char_start_dst=this2match, char_end_dst=this2end, score=0, type_id=2, tentative_name="csv_addition"

            #matchstatus = 0
            if matchtib and matchzh:
                #matchscore = 0
                matchstatus = 0
                #if Alignment.objects.filter(witness_src_id=witness_src, witness_dst_id=witness_dst, char_start_src=w1match, char_end_src=w1matchend, char_start_dst=w2match, char_end_dst=w2matchend).exists():
                #if Alignment.objects.filter(witness_src_id=witness_src, witness_dst_id=witness_dst, char_start_src=w1match, char_end_src=w1matchend).exists():
                if Alignment.objects.filter(witness_src_id=witness_src, witness_dst_id=witness_dst, char_start_src=w1match, char_start_dst=w2match).exists():

                #if Alignment.objects.filter(witness_src_id=witness_src, witness_dst_id=witness_dst).exists():
                    #kludge = 1
                    matchstatus = 1

                matches.append((w1match, w1matchlength, w1matchtarget, w1matchfound, w2match, w2matchlength, w2matchtarget, w2matchfound, matchscore, matchstatus))

                # add this alignment to the list so we can grab it back
                #csvalign = CsvAlignment(csvlist=csvlist, w1match=w1match, w1matchlength=w1matchlength, w1matchtarget=w1matchtarget, w1matchfound=w1matchfound, w2match=w2match, w2matchlength=w2matchlength, w2matchtarget=w2matchtarget, w2matchfound=w2matchfound)
                #csvalign.save()
        # elie


    # Load documents for the list page
    #documents = UserFile.objects.all()
    witnesses = Witness.objects.all()
    #alignments = Alignment.objects.all()

    # Render list page with the documents and the form
    context = {
    'csv_id': csv_id,
    'witness_src': witness_src,
    'witness_dst': witness_dst,
    'witnesses': witnesses,
    'w1content': w1content,
    'w2content': w2content,
    'w1partitions': w1partitions,
    'w2partitions': w2partitions,
    'alignments': alignments,
    #'form': form,
    'matches': matches,
    'csv_startpoint': startpoint,
    'csv_endpoint': endpoint,
    }
    return render(request, importer_template_location, context)

@login_required
def reader(request):
    error_msg = "error";
    template = loader.get_template(reader_template_location)

    context = {
    'latest_witness_list': latest_witness_list,
    'latest_alignments_list': latest_alignments_list,
    'latest_partition_list1': latest_partition_list1,
    'latest_partition_list2': latest_partition_list2,
    'latest_annotations_list1': latest_annotations_list1,
    'latest_annotations_list2': latest_annotations_list2,
    'most_recent_witness1': witness1,
    'most_recent_witness2': witness2,
    'most_recent_partition1': mrp1_id,
    'most_recent_partition2': mrp2_id,
    'partition_array': json_partition,
    'first_char1': first_char1,
    'last_char1': last_char1,
    'first_char2': first_char2,
    'last_char2': last_char2,
    'lastselection1_start': lastselection1_start,
    'lastselection1_end': lastselection1_end,
    'lastselection2_start': lastselection2_start,
    'lastselection2_end': lastselection2_end,
    'scrollvalue1': scrollvalue1,
    'scrollvalue2': scrollvalue2,
    'scrollvalue_alignments': scrollvalue_alignments,
    'usersettings': usersettings,
     }

    return HttpResponse(template.render(context, request))

#@login_required
#def alignments(request):
#    error_msg = "error";
#    template = loader.get_template(importer_template_location)

#@login_required
#def dictionaries(request):
#    error_msg = "error";
#    template = loader.get_template(importer_template_location)

@login_required
def annotations(request):
    error_msg = "error";
    template = loader.get_template(annotations_template_location)

    #usersettings = UserSettings.objects.order_by('username_id')[0]
    current_user = request.user
    usersettings = UserSettings.objects.filter(username_id=current_user.id).order_by('username_id')[0]

    scrollvalue1 = "0"
    scrollvalue2 = "0"
    scrollvalue_alignments = "0"

    latest_witness_list = Witness.objects.order_by('id')

    witness1 = latest_witness_list[0]
    witness2 = latest_witness_list[0]

    witness1_id = witness1.id
    witness2_id = witness2.id

    latest_partition_list1 = WitnessPartition.objects.filter(witness_id=witness1_id).order_by('char_start')
    latest_partition_list2 = WitnessPartition.objects.filter(witness_id=witness2_id).order_by('char_start')

    mrp1 = latest_partition_list1[0]
    mrp2 = latest_partition_list2[0]

    latest_annotations_list1 = Annotation.objects.filter(witness_id=witness1_id).order_by('char_start')
    latest_annotations_list2 = Annotation.objects.filter(witness_id=witness2_id).order_by('char_start')


    mrp1_id = mrp1.id
    mrp2_id = mrp2.id

    #latest_alignments_list = Alignment.objects.order_by('id')
    #latest_alignments_list = Alignment.objects.order_by('char_start_src')

    latest_alignments_list = Alignment.objects.filter(witness_src_id=witness1_id).filter(witness_dst_id=witness2_id).order_by('char_start_src')
    #latest_alignments_list = Alignment.objects.filter(witness_src_id=witness1_id).filter(witness_dst_id=witness2_id).order_by('char_start_src')

    partition_array =[]

    go_a1 = latest_partition_list1[0]

    if len(latest_partition_list1) > 2:
        go_b1 = latest_partition_list1[1]
        go_c1 = latest_partition_list1[2]
        new_p1 = go_a1.content + go_b1.content + go_c1.content
        last_char1 = go_c1.char_end

    elif len(latest_partition_list1) > 1:
        go_b1 = latest_partition_list1[1]
        new_p1 = go_a1.content + go_b1.content
        last_char1 = go_b1.char_end

    else:
        new_p1 = go_a1.content
        last_char1 = go_a1.char_end

    go_a2 = latest_partition_list2[0]

    if len(latest_partition_list2) > 2:
        go_b2 = latest_partition_list2[1]
        go_c2 = latest_partition_list2[2]
        new_p2 = go_a2.content + go_b2.content + go_c2.content
        last_char2 = go_c2.char_end

    elif len(latest_partition_list2) > 1:
        go_b2 = latest_partition_list2[1]
        new_p2 = go_a2.content + go_b2.content
        last_char2 = go_b2.char_end

    else:
        new_p2 = go_a2.content
        last_char2 = go_a2.char_end

    partition_array.append(new_p1)
    partition_array.append(new_p2)

    json_partition = json.dumps(partition_array)

    first_char1 = go_a1.char_start
    first_char2 = go_a2.char_start

    from1 = 0
    to1 = 0
    from2 = 0
    to2 = 0

    lastselection1_start = 0;
    lastselection1_end = 0;
    lastselection2_start = 0;
    lastselection2_end = 0;

    # if no other information given, then set base witness
    # for 1 and 2 to first available witness by ID

    if request.POST:
        post = request.POST.copy()
        reallypost = post['reallypost']
        clickstatus = post['clickstatus']

        scrollvalue1 = post['scrollvalue1']
        scrollvalue2 = post['scrollvalue2']
        scrollvalue_alignments = post['scrollvalue_alignments']

        lastselection1_start = post['lastselection1_start'];        
        lastselection1_end = post['lastselection1_end'];
        lastselection2_start = post['lastselection2_start'];
        lastselection2_end = post['lastselection2_end'];

        try:
            segnum = post['provisionaldigit']
        except ValueError:
            segnum = ""

        try:
            seglet = post['provisionalletter']
        except ValueError:
            seglet = ""

        if segnum.isdigit():
            if seglet.isalpha():
                segname = segnum + "." + seglet
            else:
                segname = segnum
        else:
            segname = ""

        try:
            witness1_id = int(post['witness1_id'])
        except ValueError:
            witness1_id = latest_witness_list[0].id

        try:
            witness2_id = int(post['witness2_id'])
        except ValueError:
            witness2_id = latest_witness_list[0].id

        witness1 = latest_witness_list.get(id=witness1_id)
        witness2 = latest_witness_list.get(id=witness2_id)

        latest_partition_list1 = WitnessPartition.objects.filter(witness_id=witness1_id).order_by('char_start')
        latest_partition_list2 = WitnessPartition.objects.filter(witness_id=witness2_id).order_by('char_start')

        latest_alignments_list = Alignment.objects.filter(witness_src_id=witness1_id).filter(witness_dst_id=witness2_id).order_by('char_start_src')

        latest_annotations_list1 = Annotation.objects.filter(witness_id=witness1_id).order_by('char_start')
        latest_annotations_list2 = Annotation.objects.filter(witness_id=witness2_id).order_by('char_start')


        mrp1 = latest_partition_list1[0]
        mrp2 = latest_partition_list2[0]

        try:
            partition1_id = int(post['partition1_id'])
        except ValueError:
            partition1_id = mrp1.id
        try:
            partition2_id = int(post['partition2_id'])
        except ValueError:
            partition2_id = mrp2.id

        mrp1_id = partition1_id
        mrp2_id = partition2_id

        from1 = post['from1']
        try:
            from1 = int(post['from1'])
        except ValueError:
            from1 = None
        try:
            to1 = int(post['to1'])
        except ValueError:
            to1 = None
        try:
            from2 = int(post['from2'])
        except ValueError:
            from2 = None

        to2 = post['to2']
        try:
            to2 = int(post['to2'])
        except ValueError:
            to2 = None

        try:
            sc = int(post['score'])
        except ValueError:
            sc = None

        partition_array =[]

        try:
            go_a1 = latest_partition_list1.get(id=mrp1_id)
        except WitnessPartition.DoesNotExist:
            go_a1 = None

        if go_a1 != None:
            if (go_a1.witness_id != witness1_id):
                go_a1 = latest_partition_list1[0]
        
            if clickstatus== "w1left":
                try:
                    go_a1 = latest_partition_list1.get(char_end=go_a1.char_start)
                except WitnessPartition.DoesNotExist:
                    pass
                mrp1_id = go_a1.id
                
            elif clickstatus== "w1right":
                try:
                    go_a1 = latest_partition_list1.get(char_start=go_a1.char_end)
                except WitnessPartition.DoesNotExist:
                    pass
                mrp1_id = go_a1.id
                
        else:
            go_a1 = latest_partition_list1[0]
        
        first_char1 = go_a1.char_start
        go_b1_start = go_a1.char_end

        try:
            go_b1 = latest_partition_list1.get(char_start=go_b1_start)
        except WitnessPartition.DoesNotExist:
            go_b1 = None

        if go_b1 != None:
            go_c1_start = go_b1.char_end
            try:
                go_c1 = latest_partition_list1.get(char_start=go_c1_start)
            except WitnessPartition.DoesNotExist:
                go_c1 = None
            
            if go_c1 != None:
                new_p1 = go_a1.content + go_b1.content + go_c1.content
                last_char1 = go_c1.char_end
            else:
                new_p1 = go_a1.content + go_b1.content
                last_char1 = go_b1.char_end
        
        else:
            new_p1 = go_a1.content
            last_char1 = go_a1.char_end
            
        ################################################
        try:
            go_a2 = latest_partition_list2.get(id=mrp2_id)
        except WitnessPartition.DoesNotExist:
            go_a2 = None

        if go_a2 != None:
            if (go_a2.witness_id != witness2_id):
                go_a2 = latest_partition_list2[0]

            if clickstatus== "w2left":
                try:
                    go_a2 = latest_partition_list2.get(char_end=go_a2.char_start)
                except WitnessPartition.DoesNotExist:
                    pass
                mrp2_id = go_a2.id
                
            elif clickstatus== "w2right":
                try:
                    go_a2 = latest_partition_list2.get(char_start=go_a2.char_end)
                except WitnessPartition.DoesNotExist:
                    pass
                mrp2_id = go_a2.id
    
        else:
            go_a2 = latest_partition_list2[0]
            
        first_char2 = go_a2.char_start
        go_b2_start = go_a2.char_end

        try:
            go_b2 = latest_partition_list2.get(char_start=go_b2_start)
        except WitnessPartition.DoesNotExist:
            go_b2 = None

        if go_b2 != None:
            go_c2_start = go_b2.char_end
            try:
                go_c2 = latest_partition_list2.get(char_start=go_c2_start)
            except WitnessPartition.DoesNotExist:
                go_c2 = None
            
            if go_c2 != None:
                new_p2 = go_a2.content + go_b2.content + go_c2.content
                last_char2 = go_c2.char_end
            else:
                new_p2 = go_a2.content + go_b2.content
                last_char2 = go_b2.char_end
        
        else:
            new_p2 = go_a2.content
            last_char2 = go_a2.char_end
            
        ################################################
        ################################################
        
        partition_array.append(new_p1)
        partition_array.append(new_p2)

        mrp1 = latest_partition_list1.get(id=mrp1_id)
        mrp2 = latest_partition_list2.get(id=mrp2_id)

        json_partition = json.dumps(partition_array)

        if (from1 != None):
            cs_src=from1 + first_char1
        else:
            cs_src=from1

        if (to1 != None):
            ce_src=to1 + first_char1
        else:
            ce_src=to1

        if (from2 != None):
            cs_dst=from2 + first_char2
        else:
            cs_dst=from2

        if (to2 != None):
            ce_dst=to2 + first_char2
        else:
            ce_dst=to2

        t_id=2
        w_src_id=witness1_id
        w_dst_id=witness2_id

        segment_name = segname

        if(reallypost == "1"):
            alignment = Alignment.objects.create(witness_src_id=w_src_id, witness_dst_id=w_dst_id, char_start_src=cs_src, char_end_src=ce_src, char_start_dst=cs_dst, char_end_dst=ce_dst, score=sc, type_id=t_id, tentative_name=segment_name)
            alignment_log = AlignmentLog.objects.create(alignment_id=alignment.id, witness_src_id=w_src_id, witness_dst_id=w_dst_id, char_start_src=cs_src, char_end_src=ce_src, char_start_dst=cs_dst, char_end_dst=ce_dst, score=sc, type_id=t_id, user_id=5)
        # end create alignment, create log object
    
    context = {
    'latest_witness_list': latest_witness_list,
    'latest_alignments_list': latest_alignments_list,
    'latest_partition_list1': latest_partition_list1,
    'latest_partition_list2': latest_partition_list2,
    'latest_annotations_list1': latest_annotations_list1,
    'latest_annotations_list2': latest_annotations_list2,
    'most_recent_witness1': witness1,
    'most_recent_witness2': witness2,
    'most_recent_partition1': mrp1_id,
    'most_recent_partition2': mrp2_id,
    'partition_array': json_partition,
    'first_char1': first_char1,
    'last_char1': last_char1,
    'first_char2': first_char2,
    'last_char2': last_char2,
    'lastselection1_start': lastselection1_start,
    'lastselection1_end': lastselection1_end,
    'lastselection2_start': lastselection2_start,
    'lastselection2_end': lastselection2_end,
    'scrollvalue1': scrollvalue1,
    'scrollvalue2': scrollvalue2,
    'scrollvalue_alignments': scrollvalue_alignments,
    'usersettings': usersettings,
     }

    return HttpResponse(template.render(context, request))

@login_required
def create_alignment(request):
    error_msg = "error";
    template = loader.get_template(alignments_template_location)

    #usersettings = UserSettings.objects.order_by('username_id')[0]
    current_user = request.user
    usersettings = UserSettings.objects.filter(username_id=current_user.id).order_by('username_id')[0]

    scrollvalue1 = "0"
    scrollvalue2 = "0"
    scrollvalue_alignments = "0"

    latest_witness_list = Witness.objects.order_by('id')

    witness1 = latest_witness_list[0]
    witness2 = latest_witness_list[0]

    witness1_id = witness1.id
    witness2_id = witness2.id

    latest_partition_list1 = WitnessPartition.objects.filter(witness_id=witness1_id).order_by('char_start')
    latest_partition_list2 = WitnessPartition.objects.filter(witness_id=witness2_id).order_by('char_start')

    mrp1 = latest_partition_list1[0]
    mrp2 = latest_partition_list2[0]

    latest_annotations_list1 = Annotation.objects.filter(witness_id=witness1_id).order_by('char_start')
    latest_annotations_list2 = Annotation.objects.filter(witness_id=witness2_id).order_by('char_start')


    mrp1_id = mrp1.id
    mrp2_id = mrp2.id

    #latest_alignments_list = Alignment.objects.filter(witness_src_id=witness1_id).filter(witness_dst_id=witness2_id).order_by('char_start_src')
    #latest_alignments_list = Alignment.objects.filter(witness_src_id=mrp1.id).order_by('char_start_src')

    #latest_alignments_list = Alignment.objects.order_by('char_start_src')
    latest_alignments_list = Alignment.objects.filter(witness_src_id=witness1_id).filter(witness_dst_id=witness2_id).order_by('char_start_src')

    #latest_alignments_text = Alignment.objects.filter(witness_src_id=witness1_id).filter(witness_dst_id=witness2_id).order_by('char_start_src')
    #the corresponding text for each alignment, to be displayed in the lower window of manual selection screen

    partition_array =[]

    go_a1 = latest_partition_list1[0]

    if len(latest_partition_list1) > 2:
        go_b1 = latest_partition_list1[1]
        go_c1 = latest_partition_list1[2]
        new_p1 = go_a1.content + go_b1.content + go_c1.content
        last_char1 = go_c1.char_end

    elif len(latest_partition_list1) > 1:
        go_b1 = latest_partition_list1[1]
        new_p1 = go_a1.content + go_b1.content
        last_char1 = go_b1.char_end

    else:
        new_p1 = go_a1.content
        last_char1 = go_a1.char_end

    go_a2 = latest_partition_list2[0]

    if len(latest_partition_list2) > 2:
        go_b2 = latest_partition_list2[1]
        go_c2 = latest_partition_list2[2]
        new_p2 = go_a2.content + go_b2.content + go_c2.content
        last_char2 = go_c2.char_end

    elif len(latest_partition_list2) > 1:
        go_b2 = latest_partition_list2[1]
        new_p2 = go_a2.content + go_b2.content
        last_char2 = go_b2.char_end

    else:
        new_p2 = go_a2.content
        last_char2 = go_a2.char_end

    partition_array.append(new_p1)
    partition_array.append(new_p2)

    json_partition = json.dumps(partition_array)

    first_char1 = go_a1.char_start
    first_char2 = go_a2.char_start

    from1 = 0
    to1 = 0
    from2 = 0
    to2 = 0

    lastselection1_start = 0;
    lastselection1_end = 0;
    lastselection2_start = 0;
    lastselection2_end = 0;

    # if no other information given, then set base witness
    # for 1 and 2 to first available witness by ID

    if request.POST:
        post = request.POST.copy()
        reallypost = post['reallypost']
        clickstatus = post['clickstatus']

        scrollvalue1 = post['scrollvalue1']
        scrollvalue2 = post['scrollvalue2']
        scrollvalue_alignments = post['scrollvalue_alignments']

        lastselection1_start = post['lastselection1_start'];        
        lastselection1_end = post['lastselection1_end'];
        lastselection2_start = post['lastselection2_start'];
        lastselection2_end = post['lastselection2_end'];

        try:
            segnum = post['provisionaldigit']
        except ValueError:
            segnum = ""

        try:
            seglet = post['provisionalletter']
        except ValueError:
            seglet = ""

        if segnum.isdigit():
            if seglet.isalpha():
                segname = segnum + "." + seglet
            else:
                segname = segnum
        else:
            segname = ""

        try:
            witness1_id = int(post['witness1_id'])
        except ValueError:
            witness1_id = latest_witness_list[0].id

        try:
            witness2_id = int(post['witness2_id'])
        except ValueError:
            witness2_id = latest_witness_list[0].id

        witness1 = latest_witness_list.get(id=witness1_id)
        witness2 = latest_witness_list.get(id=witness2_id)

        latest_partition_list1 = WitnessPartition.objects.filter(witness_id=witness1_id).order_by('char_start')
        latest_partition_list2 = WitnessPartition.objects.filter(witness_id=witness2_id).order_by('char_start')

        latest_alignments_list = Alignment.objects.filter(witness_src_id=witness1_id).filter(witness_dst_id=witness2_id).order_by('char_start_src')

        latest_annotations_list1 = Annotation.objects.filter(witness_id=witness1_id).order_by('char_start')
        latest_annotations_list2 = Annotation.objects.filter(witness_id=witness2_id).order_by('char_start')


        mrp1 = latest_partition_list1[0]
        mrp2 = latest_partition_list2[0]

        try:
            partition1_id = int(post['partition1_id'])
        except ValueError:
            partition1_id = mrp1.id
        try:
            partition2_id = int(post['partition2_id'])
        except ValueError:
            partition2_id = mrp2.id

        mrp1_id = partition1_id
        mrp2_id = partition2_id

        from1 = post['from1']
        try:
            from1 = int(post['from1'])
        except ValueError:
            from1 = None
        try:
            to1 = int(post['to1'])
        except ValueError:
            to1 = None
        try:
            from2 = int(post['from2'])
        except ValueError:
            from2 = None

        to2 = post['to2']
        try:
            to2 = int(post['to2'])
        except ValueError:
            to2 = None

        try:
            sc = int(post['score'])
        except ValueError:
            sc = None

        partition_array =[]

        try:
            go_a1 = latest_partition_list1.get(id=mrp1_id)
        except WitnessPartition.DoesNotExist:
            go_a1 = None

        if go_a1 != None:
            if (go_a1.witness_id != witness1_id):
                go_a1 = latest_partition_list1[0]
        
            if clickstatus== "w1left":
                try:
                    go_a1 = latest_partition_list1.get(char_end=go_a1.char_start)
                except WitnessPartition.DoesNotExist:
                    pass
                mrp1_id = go_a1.id
                
            elif clickstatus== "w1right":
                try:
                    go_a1 = latest_partition_list1.get(char_start=go_a1.char_end)
                except WitnessPartition.DoesNotExist:
                    pass
                mrp1_id = go_a1.id
                
        else:
            go_a1 = latest_partition_list1[0]
        
        first_char1 = go_a1.char_start
        go_b1_start = go_a1.char_end

        try:
            go_b1 = latest_partition_list1.get(char_start=go_b1_start)
        except WitnessPartition.DoesNotExist:
            go_b1 = None

        if go_b1 != None:
            go_c1_start = go_b1.char_end
            try:
                go_c1 = latest_partition_list1.get(char_start=go_c1_start)
            except WitnessPartition.DoesNotExist:
                go_c1 = None
            
            if go_c1 != None:
                new_p1 = go_a1.content + go_b1.content + go_c1.content
                last_char1 = go_c1.char_end
            else:
                new_p1 = go_a1.content + go_b1.content
                last_char1 = go_b1.char_end
        
        else:
            new_p1 = go_a1.content
            last_char1 = go_a1.char_end
            
        ################################################
        try:
            go_a2 = latest_partition_list2.get(id=mrp2_id)
        except WitnessPartition.DoesNotExist:
            go_a2 = None

        if go_a2 != None:
            if (go_a2.witness_id != witness2_id):
                go_a2 = latest_partition_list2[0]

            if clickstatus== "w2left":
                try:
                    go_a2 = latest_partition_list2.get(char_end=go_a2.char_start)
                except WitnessPartition.DoesNotExist:
                    pass
                mrp2_id = go_a2.id
                
            elif clickstatus== "w2right":
                try:
                    go_a2 = latest_partition_list2.get(char_start=go_a2.char_end)
                except WitnessPartition.DoesNotExist:
                    pass
                mrp2_id = go_a2.id
    
        else:
            go_a2 = latest_partition_list2[0]
            
        first_char2 = go_a2.char_start
        go_b2_start = go_a2.char_end

        try:
            go_b2 = latest_partition_list2.get(char_start=go_b2_start)
        except WitnessPartition.DoesNotExist:
            go_b2 = None

        if go_b2 != None:
            go_c2_start = go_b2.char_end
            try:
                go_c2 = latest_partition_list2.get(char_start=go_c2_start)
            except WitnessPartition.DoesNotExist:
                go_c2 = None
            
            if go_c2 != None:
                new_p2 = go_a2.content + go_b2.content + go_c2.content
                last_char2 = go_c2.char_end
            else:
                new_p2 = go_a2.content + go_b2.content
                last_char2 = go_b2.char_end
        
        else:
            new_p2 = go_a2.content
            last_char2 = go_a2.char_end
            
        ################################################
        ################################################
        
        partition_array.append(new_p1)
        partition_array.append(new_p2)

        mrp1 = latest_partition_list1.get(id=mrp1_id)
        mrp2 = latest_partition_list2.get(id=mrp2_id)

        json_partition = json.dumps(partition_array)

        if (from1 != None):
            cs_src=from1 + first_char1
        else:
            cs_src=from1

        if (to1 != None):
            ce_src=to1 + first_char1
        else:
            ce_src=to1

        if (from2 != None):
            cs_dst=from2 + first_char2
        else:
            cs_dst=from2

        if (to2 != None):
            ce_dst=to2 + first_char2
        else:
            ce_dst=to2

        t_id=2
        w_src_id=witness1_id
        w_dst_id=witness2_id

        segment_name = segname

        if(reallypost == "1"):
            alignment = Alignment.objects.create(witness_src_id=w_src_id, witness_dst_id=w_dst_id, char_start_src=cs_src, char_end_src=ce_src, char_start_dst=cs_dst, char_end_dst=ce_dst, score=sc, type_id=t_id, tentative_name=segment_name)
            alignment_log = AlignmentLog.objects.create(alignment_id=alignment.id, witness_src_id=w_src_id, witness_dst_id=w_dst_id, char_start_src=cs_src, char_end_src=ce_src, char_start_dst=cs_dst, char_end_dst=ce_dst, score=sc, type_id=t_id, user_id=5)
        # end create alignment, create log object
    
    context = {
    'latest_witness_list': latest_witness_list,
    'latest_alignments_list': latest_alignments_list,
    'latest_partition_list1': latest_partition_list1,
    'latest_partition_list2': latest_partition_list2,
    'latest_annotations_list1': latest_annotations_list1,
    'latest_annotations_list2': latest_annotations_list2,
    'most_recent_witness1': witness1,
    'most_recent_witness2': witness2,
    'most_recent_partition1': mrp1_id,
    'most_recent_partition2': mrp2_id,
    'partition_array': json_partition,
    'first_char1': first_char1,
    'last_char1': last_char1,
    'first_char2': first_char2,
    'last_char2': last_char2,
    'lastselection1_start': lastselection1_start,
    'lastselection1_end': lastselection1_end,
    'lastselection2_start': lastselection2_start,
    'lastselection2_end': lastselection2_end,
    'scrollvalue1': scrollvalue1,
    'scrollvalue2': scrollvalue2,
    'scrollvalue_alignments': scrollvalue_alignments,
    'usersettings': usersettings,
     }

    return HttpResponse(template.render(context, request))

@login_required
def embeddings(request):
    error_msg = "error";
    template = loader.get_template(embeddings_template_location)
    context = {
    'latest_witness_list': latest_witness_list,
    'latest_alignments_list': latest_alignments_list,
    'latest_partition_list1': latest_partition_list1,
    'latest_partition_list2': latest_partition_list2,
    'latest_annotations_list1': latest_annotations_list1,
    'latest_annotations_list2': latest_annotations_list2,
    'most_recent_witness1': witness1,
    'most_recent_witness2': witness2,
    'most_recent_partition1': mrp1_id,
    'most_recent_partition2': mrp2_id,
    'partition_array': json_partition,
    'first_char1': first_char1,
    'last_char1': last_char1,
    'first_char2': first_char2,
    'last_char2': last_char2,
    'lastselection1_start': lastselection1_start,
    'lastselection1_end': lastselection1_end,
    'lastselection2_start': lastselection2_start,
    'lastselection2_end': lastselection2_end,
    'scrollvalue1': scrollvalue1,
    'scrollvalue2': scrollvalue2,
    'scrollvalue_alignments': scrollvalue_alignments,
    'usersettings': usersettings,
     }

    return HttpResponse(template.render(context, request))

@login_required
def sts(request):
    error_msg = "error";
    template = loader.get_template(sts_template_location)
    context = {
    'latest_witness_list': latest_witness_list,
    'latest_alignments_list': latest_alignments_list,
    'latest_partition_list1': latest_partition_list1,
    'latest_partition_list2': latest_partition_list2,
    'latest_annotations_list1': latest_annotations_list1,
    'latest_annotations_list2': latest_annotations_list2,
    'most_recent_witness1': witness1,
    'most_recent_witness2': witness2,
    'most_recent_partition1': mrp1_id,
    'most_recent_partition2': mrp2_id,
    'partition_array': json_partition,
    'first_char1': first_char1,
    'last_char1': last_char1,
    'first_char2': first_char2,
    'last_char2': last_char2,
    'lastselection1_start': lastselection1_start,
    'lastselection1_end': lastselection1_end,
    'lastselection2_start': lastselection2_start,
    'lastselection2_end': lastselection2_end,
    'scrollvalue1': scrollvalue1,
    'scrollvalue2': scrollvalue2,
    'scrollvalue_alignments': scrollvalue_alignments,
    'usersettings': usersettings,
     }

    return HttpResponse(template.render(context, request))

###
# experimental
###

@login_required
def terminal(request):
    error_msg = "error";
    template = loader.get_template(terminal_template_location)

    #usersettings = UserSettings.objects.order_by('username_id')[0]

    current_user = request.user
    usersettings = UserSettings.objects.filter(username_id=current_user.id).order_by('username_id')[0]

    scrollvalue1 = "0"
    scrollvalue2 = "0"
    scrollvalue_alignments = "0"

    latest_witness_list = Witness.objects.order_by('id')

    witness1 = latest_witness_list[0]
    witness2 = latest_witness_list[0]

    witness1_id = witness1.id
    witness2_id = witness2.id

    latest_partition_list1 = WitnessPartition.objects.filter(witness_id=witness1_id).order_by('char_start')
    latest_partition_list2 = WitnessPartition.objects.filter(witness_id=witness2_id).order_by('char_start')

    mrp1 = latest_partition_list1[0]
    mrp2 = latest_partition_list2[0]

    latest_annotations_list1 = Annotation.objects.filter(witness_id=witness1_id).order_by('char_start')
    latest_annotations_list2 = Annotation.objects.filter(witness_id=witness2_id).order_by('char_start')


    mrp1_id = mrp1.id
    mrp2_id = mrp2.id

    #latest_alignments_list = Alignment.objects.order_by('id')
    #latest_alignments_list = Alignment.objects.order_by('char_start_src')
    latest_alignments_list = Alignment.objects.filter(witness_src_id=witness1_id).filter(witness_dst_id=witness2_id).order_by('char_start_src')

    partition_array =[]

    go_a1 = latest_partition_list1[0]

    if len(latest_partition_list1) > 2:
        go_b1 = latest_partition_list1[1]
        go_c1 = latest_partition_list1[2]
        new_p1 = go_a1.content + go_b1.content + go_c1.content
        last_char1 = go_c1.char_end

    elif len(latest_partition_list1) > 1:
        go_b1 = latest_partition_list1[1]
        new_p1 = go_a1.content + go_b1.content
        last_char1 = go_b1.char_end

    else:
        new_p1 = go_a1.content
        last_char1 = go_a1.char_end

    go_a2 = latest_partition_list2[0]

    if len(latest_partition_list2) > 2:
        go_b2 = latest_partition_list2[1]
        go_c2 = latest_partition_list2[2]
        new_p2 = go_a2.content + go_b2.content + go_c2.content
        last_char2 = go_c2.char_end

    elif len(latest_partition_list2) > 1:
        go_b2 = latest_partition_list2[1]
        new_p2 = go_a2.content + go_b2.content
        last_char2 = go_b2.char_end

    else:
        new_p2 = go_a2.content
        last_char2 = go_a2.char_end

    partition_array.append(new_p1)
    partition_array.append(new_p2)

    json_partition = json.dumps(partition_array)

    first_char1 = go_a1.char_start
    first_char2 = go_a2.char_start

    from1 = 0
    to1 = 0
    from2 = 0
    to2 = 0

    lastselection1_start = 0;
    lastselection1_end = 0;
    lastselection2_start = 0;
    lastselection2_end = 0;

    # if no other information given, then set base witness
    # for 1 and 2 to first available witness by ID

    if request.POST:
        post = request.POST.copy()
        reallypost = post['reallypost']
        clickstatus = post['clickstatus']

        scrollvalue1 = post['scrollvalue1']
        scrollvalue2 = post['scrollvalue2']
        scrollvalue_alignments = post['scrollvalue_alignments']

        lastselection1_start = post['lastselection1_start'];        
        lastselection1_end = post['lastselection1_end'];
        lastselection2_start = post['lastselection2_start'];
        lastselection2_end = post['lastselection2_end'];

        try:
            witness1_id = int(post['witness1_id'])
        except ValueError:
            witness1_id = latest_witness_list[0].id

        try:
            witness2_id = int(post['witness2_id'])
        except ValueError:
            witness2_id = latest_witness_list[0].id

        witness1 = latest_witness_list.get(id=witness1_id)
        witness2 = latest_witness_list.get(id=witness2_id)

        latest_partition_list1 = WitnessPartition.objects.filter(witness_id=witness1_id).order_by('char_start')
        latest_partition_list2 = WitnessPartition.objects.filter(witness_id=witness2_id).order_by('char_start')

        #latest_alignments_list = Alignment.objects.filter(witness_src_id=witness1_id).order_by('char_start_src')
        latest_alignments_list = Alignment.objects.filter(witness_src_id=witness1_id).filter(witness_dst_id=witness2_id).order_by('char_start_src')

        latest_annotations_list1 = Annotation.objects.filter(witness_id=witness1_id).order_by('char_start')
        latest_annotations_list2 = Annotation.objects.filter(witness_id=witness2_id).order_by('char_start')


        mrp1 = latest_partition_list1[0]
        mrp2 = latest_partition_list2[0]

        try:
            partition1_id = int(post['partition1_id'])
        except ValueError:
            partition1_id = mrp1.id
        try:
            partition2_id = int(post['partition2_id'])
        except ValueError:
            partition2_id = mrp2.id

        mrp1_id = partition1_id
        mrp2_id = partition2_id

        from1 = post['from1']
        try:
            from1 = int(post['from1'])
        except ValueError:
            from1 = None
        try:
            to1 = int(post['to1'])
        except ValueError:
            to1 = None
        try:
            from2 = int(post['from2'])
        except ValueError:
            from2 = None

        to2 = post['to2']
        try:
            to2 = int(post['to2'])
        except ValueError:
            to2 = None

        try:
            sc = int(post['score'])
        except ValueError:
            sc = None

        partition_array =[]

        try:
            go_a1 = latest_partition_list1.get(id=mrp1_id)
        except WitnessPartition.DoesNotExist:
            go_a1 = None

        if go_a1 != None:
            if (go_a1.witness_id != witness1_id):
                go_a1 = latest_partition_list1[0]
        
            if clickstatus== "w1left":
                try:
                    go_a1 = latest_partition_list1.get(char_end=go_a1.char_start)
                except WitnessPartition.DoesNotExist:
                    pass
                mrp1_id = go_a1.id
                
            elif clickstatus== "w1right":
                try:
                    go_a1 = latest_partition_list1.get(char_start=go_a1.char_end)
                except WitnessPartition.DoesNotExist:
                    pass
                mrp1_id = go_a1.id
                
        else:
            go_a1 = latest_partition_list1[0]
        
        first_char1 = go_a1.char_start
        go_b1_start = go_a1.char_end

        try:
            go_b1 = latest_partition_list1.get(char_start=go_b1_start)
        except WitnessPartition.DoesNotExist:
            go_b1 = None

        if go_b1 != None:
            go_c1_start = go_b1.char_end
            try:
                go_c1 = latest_partition_list1.get(char_start=go_c1_start)
            except WitnessPartition.DoesNotExist:
                go_c1 = None
            
            if go_c1 != None:
                new_p1 = go_a1.content + go_b1.content + go_c1.content
                last_char1 = go_c1.char_end
            else:
                new_p1 = go_a1.content + go_b1.content
                last_char1 = go_b1.char_end
        
        else:
            new_p1 = go_a1.content
            last_char1 = go_a1.char_end
            
        ################################################
        try:
            go_a2 = latest_partition_list2.get(id=mrp2_id)
        except WitnessPartition.DoesNotExist:
            go_a2 = None

        if go_a2 != None:
            if (go_a2.witness_id != witness2_id):
                go_a2 = latest_partition_list2[0]

            if clickstatus== "w2left":
                try:
                    go_a2 = latest_partition_list2.get(char_end=go_a2.char_start)
                except WitnessPartition.DoesNotExist:
                    pass
                mrp2_id = go_a2.id
                
            elif clickstatus== "w2right":
                try:
                    go_a2 = latest_partition_list2.get(char_start=go_a2.char_end)
                except WitnessPartition.DoesNotExist:
                    pass
                mrp2_id = go_a2.id
    
        else:
            go_a2 = latest_partition_list2[0]
            
        first_char2 = go_a2.char_start
        go_b2_start = go_a2.char_end

        try:
            go_b2 = latest_partition_list2.get(char_start=go_b2_start)
        except WitnessPartition.DoesNotExist:
            go_b2 = None

        if go_b2 != None:
            go_c2_start = go_b2.char_end
            try:
                go_c2 = latest_partition_list2.get(char_start=go_c2_start)
            except WitnessPartition.DoesNotExist:
                go_c2 = None
            
            if go_c2 != None:
                new_p2 = go_a2.content + go_b2.content + go_c2.content
                last_char2 = go_c2.char_end
            else:
                new_p2 = go_a2.content + go_b2.content
                last_char2 = go_b2.char_end
        
        else:
            new_p2 = go_a2.content
            last_char2 = go_a2.char_end
            
        ################################################
        ################################################
        
        partition_array.append(new_p1)
        partition_array.append(new_p2)

        mrp1 = latest_partition_list1.get(id=mrp1_id)
        mrp2 = latest_partition_list2.get(id=mrp2_id)

        json_partition = json.dumps(partition_array)

        if (from1 != None):
            cs_src=from1 + first_char1
        else:
            cs_src=from1

        if (to1 != None):
            ce_src=to1 + first_char1
        else:
            ce_src=to1

        if (from2 != None):
            cs_dst=from2 + first_char2
        else:
            cs_dst=from2

        if (to2 != None):
            ce_dst=to2 + first_char2
        else:
            ce_dst=to2

        t_id=2
        w_src_id=witness1_id
        w_dst_id=witness2_id
        
        if(reallypost == "1"):
            alignment = Alignment.objects.create(witness_src_id=w_src_id, witness_dst_id=w_dst_id, char_start_src=cs_src, char_end_src=ce_src, char_start_dst=cs_dst, char_end_dst=ce_dst, score=sc, type_id=t_id)
            alignment_log = AlignmentLog.objects.create(alignment_id=alignment.id, witness_src_id=w_src_id, witness_dst_id=w_dst_id, char_start_src=cs_src, char_end_src=ce_src, char_start_dst=cs_dst, char_end_dst=ce_dst, score=sc, type_id=t_id, user_id=5)
        # end create alignment, create log object
    
    context = {
    'latest_witness_list': latest_witness_list,
    'latest_alignments_list': latest_alignments_list,
    'latest_partition_list1': latest_partition_list1,
    'latest_partition_list2': latest_partition_list2,
    'latest_annotations_list1': latest_annotations_list1,
    'latest_annotations_list2': latest_annotations_list2,
    'most_recent_witness1': witness1,
    'most_recent_witness2': witness2,
    'most_recent_partition1': mrp1_id,
    'most_recent_partition2': mrp2_id,
    'partition_array': json_partition,
    'first_char1': first_char1,
    'last_char1': last_char1,
    'first_char2': first_char2,
    'last_char2': last_char2,
    'lastselection1_start': lastselection1_start,
    'lastselection1_end': lastselection1_end,
    'lastselection2_start': lastselection2_start,
    'lastselection2_end': lastselection2_end,
    'scrollvalue1': scrollvalue1,
    'scrollvalue2': scrollvalue2,
    'scrollvalue_alignments': scrollvalue_alignments,
    'usersettings': usersettings,
     }

    return HttpResponse(template.render(context, request))

@login_required
def visualisations(request):
    error_msg = "error";
    template = loader.get_template(visualisations_template_location)
    context = {
    'latest_witness_list': latest_witness_list,
    'latest_alignments_list': latest_alignments_list,
    'latest_partition_list1': latest_partition_list1,
    'latest_partition_list2': latest_partition_list2,
    'latest_annotations_list1': latest_annotations_list1,
    'latest_annotations_list2': latest_annotations_list2,
    'most_recent_witness1': witness1,
    'most_recent_witness2': witness2,
    'most_recent_partition1': mrp1_id,
    'most_recent_partition2': mrp2_id,
    'partition_array': json_partition,
    'first_char1': first_char1,
    'last_char1': last_char1,
    'first_char2': first_char2,
    'last_char2': last_char2,
    'lastselection1_start': lastselection1_start,
    'lastselection1_end': lastselection1_end,
    'lastselection2_start': lastselection2_start,
    'lastselection2_end': lastselection2_end,
    'scrollvalue1': scrollvalue1,
    'scrollvalue2': scrollvalue2,
    'scrollvalue_alignments': scrollvalue_alignments,
    'usersettings': usersettings,
     }

    return HttpResponse(template.render(context, request))

#@login_required
#def settings(request):
#    error_msg = "error";
#    template = loader.get_template(importer_template_location)

@login_required
def dictionaries(request):
    error_msg = "error";
    template = loader.get_template(dictionaries_template_location)

    #usersettings = UserSettings.objects.order_by('username_id')[0]

    current_user = request.user
    usersettings = UserSettings.objects.filter(username_id=current_user.id).order_by('username_id')[0]


    scrollvalue1 = "0"
    scrollvalue2 = "0"
    scrollvalue_alignments = "0"

    latest_witness_list = Witness.objects.order_by('id')

    witness1 = latest_witness_list[0]
    witness2 = latest_witness_list[0]

    witness1_id = witness1.id
    witness2_id = witness2.id

    latest_partition_list1 = WitnessPartition.objects.filter(witness_id=witness1_id).order_by('char_start')
    latest_partition_list2 = WitnessPartition.objects.filter(witness_id=witness2_id).order_by('char_start')

    mrp1 = latest_partition_list1[0]
    mrp2 = latest_partition_list2[0]

    latest_annotations_list1 = Annotation.objects.filter(witness_id=witness1_id).order_by('char_start')
    latest_annotations_list2 = Annotation.objects.filter(witness_id=witness2_id).order_by('char_start')


    mrp1_id = mrp1.id
    mrp2_id = mrp2.id

    #latest_alignments_list = Alignment.objects.order_by('id')
    #latest_alignments_list = Alignment.objects.order_by('char_start_src')
    latest_alignments_list = Alignment.objects.filter(witness_src_id=witness1_id).filter(witness_dst_id=witness2_id).order_by('char_start_src')

    partition_array =[]

    go_a1 = latest_partition_list1[0]

    if len(latest_partition_list1) > 2:
        go_b1 = latest_partition_list1[1]
        go_c1 = latest_partition_list1[2]
        new_p1 = go_a1.content + go_b1.content + go_c1.content
        last_char1 = go_c1.char_end

    elif len(latest_partition_list1) > 1:
        go_b1 = latest_partition_list1[1]
        new_p1 = go_a1.content + go_b1.content
        last_char1 = go_b1.char_end

    else:
        new_p1 = go_a1.content
        last_char1 = go_a1.char_end

    go_a2 = latest_partition_list2[0]

    if len(latest_partition_list2) > 2:
        go_b2 = latest_partition_list2[1]
        go_c2 = latest_partition_list2[2]
        new_p2 = go_a2.content + go_b2.content + go_c2.content
        last_char2 = go_c2.char_end

    elif len(latest_partition_list2) > 1:
        go_b2 = latest_partition_list2[1]
        new_p2 = go_a2.content + go_b2.content
        last_char2 = go_b2.char_end

    else:
        new_p2 = go_a2.content
        last_char2 = go_a2.char_end

    partition_array.append(new_p1)
    partition_array.append(new_p2)

    json_partition = json.dumps(partition_array)

    first_char1 = go_a1.char_start
    first_char2 = go_a2.char_start

    from1 = 0
    to1 = 0
    from2 = 0
    to2 = 0

    lastselection1_start = 0;
    lastselection1_end = 0;
    lastselection2_start = 0;
    lastselection2_end = 0;

    # if no other information given, then set base witness
    # for 1 and 2 to first available witness by ID

    if request.POST:
        post = request.POST.copy()
        reallypost = post['reallypost']
        clickstatus = post['clickstatus']

        scrollvalue1 = post['scrollvalue1']
        scrollvalue2 = post['scrollvalue2']
        scrollvalue_alignments = post['scrollvalue_alignments']

        lastselection1_start = post['lastselection1_start'];        
        lastselection1_end = post['lastselection1_end'];
        lastselection2_start = post['lastselection2_start'];
        lastselection2_end = post['lastselection2_end'];

        try:
            witness1_id = int(post['witness1_id'])
        except ValueError:
            witness1_id = latest_witness_list[0].id

        try:
            witness2_id = int(post['witness2_id'])
        except ValueError:
            witness2_id = latest_witness_list[0].id

        witness1 = latest_witness_list.get(id=witness1_id)
        witness2 = latest_witness_list.get(id=witness2_id)

        latest_partition_list1 = WitnessPartition.objects.filter(witness_id=witness1_id).order_by('char_start')
        latest_partition_list2 = WitnessPartition.objects.filter(witness_id=witness2_id).order_by('char_start')

        #latest_alignments_list = Alignment.objects.filter(witness_src_id=witness1_id).order_by('char_start_src')
        latest_alignments_list = Alignment.objects.filter(witness_src_id=witness1_id).filter(witness_dst_id=witness2_id).order_by('char_start_src')

        latest_annotations_list1 = Annotation.objects.filter(witness_id=witness1_id).order_by('char_start')
        latest_annotations_list2 = Annotation.objects.filter(witness_id=witness2_id).order_by('char_start')


        mrp1 = latest_partition_list1[0]
        mrp2 = latest_partition_list2[0]

        try:
            partition1_id = int(post['partition1_id'])
        except ValueError:
            partition1_id = mrp1.id
        try:
            partition2_id = int(post['partition2_id'])
        except ValueError:
            partition2_id = mrp2.id

        mrp1_id = partition1_id
        mrp2_id = partition2_id

        from1 = post['from1']
        try:
            from1 = int(post['from1'])
        except ValueError:
            from1 = None
        try:
            to1 = int(post['to1'])
        except ValueError:
            to1 = None
        try:
            from2 = int(post['from2'])
        except ValueError:
            from2 = None

        to2 = post['to2']
        try:
            to2 = int(post['to2'])
        except ValueError:
            to2 = None

        try:
            sc = int(post['score'])
        except ValueError:
            sc = None

        partition_array =[]

        try:
            go_a1 = latest_partition_list1.get(id=mrp1_id)
        except WitnessPartition.DoesNotExist:
            go_a1 = None

        if go_a1 != None:
            if (go_a1.witness_id != witness1_id):
                go_a1 = latest_partition_list1[0]
        
            if clickstatus== "w1left":
                try:
                    go_a1 = latest_partition_list1.get(char_end=go_a1.char_start)
                except WitnessPartition.DoesNotExist:
                    pass
                mrp1_id = go_a1.id
                
            elif clickstatus== "w1right":
                try:
                    go_a1 = latest_partition_list1.get(char_start=go_a1.char_end)
                except WitnessPartition.DoesNotExist:
                    pass
                mrp1_id = go_a1.id
                
        else:
            go_a1 = latest_partition_list1[0]
        
        first_char1 = go_a1.char_start
        go_b1_start = go_a1.char_end

        try:
            go_b1 = latest_partition_list1.get(char_start=go_b1_start)
        except WitnessPartition.DoesNotExist:
            go_b1 = None

        if go_b1 != None:
            go_c1_start = go_b1.char_end
            try:
                go_c1 = latest_partition_list1.get(char_start=go_c1_start)
            except WitnessPartition.DoesNotExist:
                go_c1 = None
            
            if go_c1 != None:
                new_p1 = go_a1.content + go_b1.content + go_c1.content
                last_char1 = go_c1.char_end
            else:
                new_p1 = go_a1.content + go_b1.content
                last_char1 = go_b1.char_end
        
        else:
            new_p1 = go_a1.content
            last_char1 = go_a1.char_end
            
        ################################################
        try:
            go_a2 = latest_partition_list2.get(id=mrp2_id)
        except WitnessPartition.DoesNotExist:
            go_a2 = None

        if go_a2 != None:
            if (go_a2.witness_id != witness2_id):
                go_a2 = latest_partition_list2[0]

            if clickstatus== "w2left":
                try:
                    go_a2 = latest_partition_list2.get(char_end=go_a2.char_start)
                except WitnessPartition.DoesNotExist:
                    pass
                mrp2_id = go_a2.id
                
            elif clickstatus== "w2right":
                try:
                    go_a2 = latest_partition_list2.get(char_start=go_a2.char_end)
                except WitnessPartition.DoesNotExist:
                    pass
                mrp2_id = go_a2.id
    
        else:
            go_a2 = latest_partition_list2[0]
            
        first_char2 = go_a2.char_start
        go_b2_start = go_a2.char_end

        try:
            go_b2 = latest_partition_list2.get(char_start=go_b2_start)
        except WitnessPartition.DoesNotExist:
            go_b2 = None

        if go_b2 != None:
            go_c2_start = go_b2.char_end
            try:
                go_c2 = latest_partition_list2.get(char_start=go_c2_start)
            except WitnessPartition.DoesNotExist:
                go_c2 = None
            
            if go_c2 != None:
                new_p2 = go_a2.content + go_b2.content + go_c2.content
                last_char2 = go_c2.char_end
            else:
                new_p2 = go_a2.content + go_b2.content
                last_char2 = go_b2.char_end
        
        else:
            new_p2 = go_a2.content
            last_char2 = go_a2.char_end
            
        ################################################
        ################################################
        
        partition_array.append(new_p1)
        partition_array.append(new_p2)

        mrp1 = latest_partition_list1.get(id=mrp1_id)
        mrp2 = latest_partition_list2.get(id=mrp2_id)

        json_partition = json.dumps(partition_array)

        if (from1 != None):
            cs_src=from1 + first_char1
        else:
            cs_src=from1

        if (to1 != None):
            ce_src=to1 + first_char1
        else:
            ce_src=to1

        if (from2 != None):
            cs_dst=from2 + first_char2
        else:
            cs_dst=from2

        if (to2 != None):
            ce_dst=to2 + first_char2
        else:
            ce_dst=to2

        t_id=2
        w_src_id=witness1_id
        w_dst_id=witness2_id
        
        segment_name = segname

        if(reallypost == "1"):
            alignment = Alignment.objects.create(witness_src_id=w_src_id, witness_dst_id=w_dst_id, char_start_src=cs_src, char_end_src=ce_src, char_start_dst=cs_dst, char_end_dst=ce_dst, score=sc, type_id=t_id, tentative_name=segment_name)
            alignment_log = AlignmentLog.objects.create(alignment_id=alignment.id, witness_src_id=w_src_id, witness_dst_id=w_dst_id, char_start_src=cs_src, char_end_src=ce_src, char_start_dst=cs_dst, char_end_dst=ce_dst, score=sc, type_id=t_id, user_id=5)
        # end create alignment, create log object
    
    context = {
    'latest_witness_list': latest_witness_list,
    'latest_alignments_list': latest_alignments_list,
    'latest_partition_list1': latest_partition_list1,
    'latest_partition_list2': latest_partition_list2,
    'latest_annotations_list1': latest_annotations_list1,
    'latest_annotations_list2': latest_annotations_list2,
    'most_recent_witness1': witness1,
    'most_recent_witness2': witness2,
    'most_recent_partition1': mrp1_id,
    'most_recent_partition2': mrp2_id,
    'partition_array': json_partition,
    'first_char1': first_char1,
    'last_char1': last_char1,
    'first_char2': first_char2,
    'last_char2': last_char2,
    'lastselection1_start': lastselection1_start,
    'lastselection1_end': lastselection1_end,
    'lastselection2_start': lastselection2_start,
    'lastselection2_end': lastselection2_end,
    'scrollvalue1': scrollvalue1,
    'scrollvalue2': scrollvalue2,
    'scrollvalue_alignments': scrollvalue_alignments,
    'usersettings': usersettings,
     }

    return HttpResponse(template.render(context, request))

@login_required
def update_alignment(request):
   
    error_msg = "error";
    template = loader.get_template(alignments_template_location)

    #usersettings = UserSettings.objects.order_by('username_id')[0]
    current_user = request.user
    usersettings = UserSettings.objects.filter(username_id=current_user.id).order_by('username_id')[0]


    scrollvalue1 = "0"
    scrollvalue2 = "0"
    scrollvalue_alignments = "0"

    latest_witness_list = Witness.objects.order_by('id')
    latest_alignments_list = Alignment.objects.order_by('char_start_src')
    #latest_alignments_list = Alignment.objects.filter(witness_src_id=witness1_id).filter(witness_dst_id=witness2_id).order_by('char_start_src')

    from1 = 0
    to1 = 0
    from2 = 0
    to2 = 0

    lastselection1_start = 0
    lastselection1_end = 0
    lastselection2_start = 0
    lastselection2_end = 0
   
    post = request.POST.copy()
    alignment_id = int(post['alignment_id'])
    revisedscore = int(post['revisedscore'])

    #
    reallypost = 0
    #clickstatus = post['clickstatus']

    scrollvalue1 = post['scrollvalue1']
    scrollvalue2 = post['scrollvalue2']
    scrollvalue_alignments = post['scrollvalue_alignments']

    try:
        witness1_id = int(post['witness1_id'])
    except ValueError:
        witness1_id = latest_witness_list[0].id

    try:
        witness2_id = int(post['witness2_id'])
    except ValueError:
        witness2_id = latest_witness_list[0].id

    witness1 = latest_witness_list.get(id=witness1_id)
    witness2 = latest_witness_list.get(id=witness2_id)

    latest_partition_list1 = WitnessPartition.objects.filter(witness_id=witness1_id).order_by('char_start')
    latest_partition_list2 = WitnessPartition.objects.filter(witness_id=witness2_id).order_by('char_start')

    #latest_alignments_list = Alignment.objects.filter(witness_src_id=witness1_id).order_by('char_start_src')
    latest_alignments_list = Alignment.objects.filter(witness_src_id=witness1_id).filter(witness_dst_id=witness2_id).order_by('char_start_src')

    latest_annotations_list1 = Annotation.objects.filter(witness_id=witness1_id).order_by('char_start')
    latest_annotations_list2 = Annotation.objects.filter(witness_id=witness2_id).order_by('char_start')


    try:
        partition1_id = int(post['partition1_id'])
    except ValueError:
        partition1_id = mrp1.id
    try:
        partition2_id = int(post['partition2_id'])
    except ValueError:
        partition2_id = mrp2.id

    mrp1_id = partition1_id
    mrp2_id = partition2_id
    #
    one_entry = latest_alignments_list.get(id=alignment_id)

    one_entry.score = revisedscore
    one_entry.save()

    # new_log_entry =
    ### ADD NEW LOG ENTRY TO RECORD CHANGE
    #alignment = Alignment.objects.create(witness_src_id=w_src_id, witness_dst_id=w_dst_id, char_start_src=cs_src, char_end_src=ce_src, char_start_dst=cs_dst, char_end_dst=ce_dst, score=sc, type_id=t_id)
    
    #alignment_log = AlignmentLog.objects.create(alignment_id=alignment.id, witness_src_id=w_src_id, witness_dst_id=w_dst_id, char_start_src=cs_src, char_end_src=ce_src, char_start_dst=cs_dst, char_end_dst=ce_dst, score=sc, type_id=t_id, user_id=5)

    #latest_alignments_list = Alignment.objects.order_by('char_start_src')
    latest_alignments_list = Alignment.objects.filter(witness_src_id=witness1_id).filter(witness_dst_id=witness2_id).order_by('char_start_src')


    partition_array =[]

    go_a1 = latest_partition_list1[0]

    if len(latest_partition_list1) > 2:
        go_b1 = latest_partition_list1[1]
        go_c1 = latest_partition_list1[2]
        new_p1 = go_a1.content + go_b1.content + go_c1.content
        last_char1 = go_c1.char_end

    elif len(latest_partition_list1) > 1:
        go_b1 = latest_partition_list1[1]
        new_p1 = go_a1.content + go_b1.content
        last_char1 = go_b1.char_end

    else:
        new_p1 = go_a1.content
        last_char1 = go_a1.char_end

    go_a2 = latest_partition_list2[0]

    if len(latest_partition_list2) > 2:
        go_b2 = latest_partition_list2[1]
        go_c2 = latest_partition_list2[2]
        new_p2 = go_a2.content + go_b2.content + go_c2.content
        last_char2 = go_c2.char_end

    elif len(latest_partition_list2) > 1:
        go_b2 = latest_partition_list2[1]
        new_p2 = go_a2.content + go_b2.content
        last_char2 = go_b2.char_end

    else:
        new_p2 = go_a2.content
        last_char2 = go_a2.char_end

    partition_array.append(new_p1)
    partition_array.append(new_p2)

    json_partition = json.dumps(partition_array)

    first_char1 = go_a1.char_start
    first_char2 = go_a2.char_start


    #one_entry.save(update_fields=['score'])
    #alignment = Alignment.objects.update(score=sc)

    #alignment.update(blog=b)

    #alignment = Alignment.objects.update(blog=b)

    #(witness_src_id=w_src_id, witness_dst_id=w_dst_id, char_start_src=cs_src, char_end_src=ce_src, char_start_dst=cs_dst, char_end_dst=ce_dst, score=revisedscore, type_id=t_id)

    #alignment_log = AlignmentLog.objects.create(alignment_id=alignment.id, witness_src_id=w_src_id, witness_dst_id=w_dst_id, char_start_src=cs_src, char_end_src=ce_src, char_start_dst=cs_dst, char_end_dst=ce_dst, score=sc, type_id=t_id, user_id=5)

    context = {
    'latest_witness_list': latest_witness_list,
    'latest_alignments_list': latest_alignments_list,
    'latest_partition_list1': latest_partition_list1,
    'latest_partition_list2': latest_partition_list2,
    'latest_annotations_list1': latest_annotations_list1,
    'latest_annotations_list2': latest_annotations_list2,
    'most_recent_witness1': witness1,
    'most_recent_witness2': witness2,
    'most_recent_partition1': mrp1_id,
    'most_recent_partition2': mrp2_id,
    'partition_array': json_partition,
    'first_char1': first_char1,
    'last_char1': last_char1,
    'first_char2': first_char2,
    'last_char2': last_char2,
    'lastselection1_start': lastselection1_start,
    'lastselection1_end': lastselection1_end,
    'lastselection2_start': lastselection2_start,
    'lastselection2_end': lastselection2_end,
    'scrollvalue1': scrollvalue1,
    'scrollvalue2': scrollvalue2,
    'scrollvalue_alignments': scrollvalue_alignments,
    'usersettings': usersettings,
     }
    return HttpResponse(template.render(context, request))

@login_required
def delete_alignment(request):
   
    error_msg = "error";
    template = loader.get_template(alignments_template_location)

    #usersettings = UserSettings.objects.order_by('username_id')[0]
    current_user = request.user
    usersettings = UserSettings.objects.filter(username_id=current_user.id).order_by('username_id')[0]


    scrollvalue1 = "0"
    scrollvalue2 = "0"
    scrollvalue_alignments = "0"

    latest_witness_list = Witness.objects.order_by('id')

    witness1 = latest_witness_list[0]
    witness2 = latest_witness_list[0]

    witness1_id = witness1.id
    witness2_id = witness2.id

    latest_alignments_list = Alignment.objects.order_by('char_start_src')
    #latest_alignments_list = Alignment.objects.filter(witness_src_id=witness1_id).filter(witness_dst_id=witness2_id).order_by('char_start_src')

    from1 = 0
    to1 = 0
    from2 = 0
    to2 = 0

    lastselection1_start = 0
    lastselection1_end = 0
    lastselection2_start = 0
    lastselection2_end = 0
   
    post = request.POST.copy()
    alignment_id = int(post['alignment_id'])
    #revisedscore = int(post['revisedscore'])

    #
    reallypost = 0
    #clickstatus = post['clickstatus']

    scrollvalue1 = post['scrollvalue1']
    scrollvalue2 = post['scrollvalue2']
    scrollvalue_alignments = post['scrollvalue_alignments']

    try:
        witness1_id = int(post['witness1_id'])
    except ValueError:
        witness1_id = latest_witness_list[0].id

    try:
        witness2_id = int(post['witness2_id'])
    except ValueError:
        witness2_id = latest_witness_list[0].id

    witness1 = latest_witness_list.get(id=witness1_id)
    witness2 = latest_witness_list.get(id=witness2_id)

    latest_partition_list1 = WitnessPartition.objects.filter(witness_id=witness1_id).order_by('char_start')
    latest_partition_list2 = WitnessPartition.objects.filter(witness_id=witness2_id).order_by('char_start')

    mrp1 = latest_partition_list1[0]
    mrp2 = latest_partition_list2[0]


    latest_annotations_list1 = Annotation.objects.filter(witness_id=witness1_id).order_by('char_start')
    latest_annotations_list2 = Annotation.objects.filter(witness_id=witness2_id).order_by('char_start')


    try:
        partition1_id = int(post['partition1_id'])
    except ValueError:
        partition1_id = mrp1.id
    try:
        partition2_id = int(post['partition2_id'])
    except ValueError:
        partition2_id = mrp2.id

    mrp1_id = partition1_id
    mrp2_id = partition2_id
    #
    
    instance = latest_alignments_list.get(id=alignment_id)
    instance.delete()
    #one_entry = latest_alignments_list.get(id=alignment_id)
    #one_entry.score = revisedscore
    #one_entry.save()

    # new_log_entry =
    ### ADD NEW LOG ENTRY TO RECORD CHANGE
    #alignment = Alignment.objects.create(witness_src_id=w_src_id, witness_dst_id=w_dst_id, char_start_src=cs_src, char_end_src=ce_src, char_start_dst=cs_dst, char_end_dst=ce_dst, score=sc, type_id=t_id)
    
    #alignment_log = AlignmentLog.objects.create(alignment_id=alignment.id, witness_src_id=w_src_id, witness_dst_id=w_dst_id, char_start_src=cs_src, char_end_src=ce_src, char_start_dst=cs_dst, char_end_dst=ce_dst, score=sc, type_id=t_id, user_id=5)

    #latest_alignments_list = Alignment.objects.order_by('char_start_src')
    latest_alignments_list = Alignment.objects.filter(witness_src_id=witness1_id).filter(witness_dst_id=witness2_id).order_by('char_start_src')


    partition_array =[]

    go_a1 = latest_partition_list1[0]

    if len(latest_partition_list1) > 2:
        go_b1 = latest_partition_list1[1]
        go_c1 = latest_partition_list1[2]
        new_p1 = go_a1.content + go_b1.content + go_c1.content
        last_char1 = go_c1.char_end

    elif len(latest_partition_list1) > 1:
        go_b1 = latest_partition_list1[1]
        new_p1 = go_a1.content + go_b1.content
        last_char1 = go_b1.char_end

    else:
        new_p1 = go_a1.content
        last_char1 = go_a1.char_end

    go_a2 = latest_partition_list2[0]

    if len(latest_partition_list2) > 2:
        go_b2 = latest_partition_list2[1]
        go_c2 = latest_partition_list2[2]
        new_p2 = go_a2.content + go_b2.content + go_c2.content
        last_char2 = go_c2.char_end

    elif len(latest_partition_list2) > 1:
        go_b2 = latest_partition_list2[1]
        new_p2 = go_a2.content + go_b2.content
        last_char2 = go_b2.char_end

    else:
        new_p2 = go_a2.content
        last_char2 = go_a2.char_end

    partition_array.append(new_p1)
    partition_array.append(new_p2)

    json_partition = json.dumps(partition_array)

    first_char1 = go_a1.char_start
    first_char2 = go_a2.char_start


    #one_entry.save(update_fields=['score'])
    #alignment = Alignment.objects.update(score=sc)

    #alignment.update(blog=b)

    #alignment = Alignment.objects.update(blog=b)

    #(witness_src_id=w_src_id, witness_dst_id=w_dst_id, char_start_src=cs_src, char_end_src=ce_src, char_start_dst=cs_dst, char_end_dst=ce_dst, score=revisedscore, type_id=t_id)

    #alignment_log = AlignmentLog.objects.create(alignment_id=alignment.id, witness_src_id=w_src_id, witness_dst_id=w_dst_id, char_start_src=cs_src, char_end_src=ce_src, char_start_dst=cs_dst, char_end_dst=ce_dst, score=sc, type_id=t_id, user_id=5)

    context = {
    'latest_witness_list': latest_witness_list,
    'latest_alignments_list': latest_alignments_list,
    'latest_partition_list1': latest_partition_list1,
    'latest_partition_list2': latest_partition_list2,
    'latest_annotations_list1': latest_annotations_list1,
    'latest_annotations_list2': latest_annotations_list2,
    'most_recent_witness1': witness1,
    'most_recent_witness2': witness2,
    'most_recent_partition1': mrp1_id,
    'most_recent_partition2': mrp2_id,
    'partition_array': json_partition,
    'first_char1': first_char1,
    'last_char1': last_char1,
    'first_char2': first_char2,
    'last_char2': last_char2,
    'lastselection1_start': lastselection1_start,
    'lastselection1_end': lastselection1_end,
    'lastselection2_start': lastselection2_start,
    'lastselection2_end': lastselection2_end,
    'scrollvalue1': scrollvalue1,
    'scrollvalue2': scrollvalue2,
    'scrollvalue_alignments': scrollvalue_alignments,
    'usersettings': usersettings,
     }
    return HttpResponse(template.render(context, request))

@login_required
def settings(request):
    error_msg = "error";
    template = loader.get_template(settings_template_location)

    #usersettings = UserSettings.objects.order_by('username_id')[0]

    current_user = request.user
    usersettings = UserSettings.objects.filter(username_id=current_user.id).order_by('username_id')[0]

    scrollvalue1 = "0"
    scrollvalue2 = "0"
    scrollvalue_alignments = "0"

    latest_witness_list = Witness.objects.order_by('id')

    witness1 = latest_witness_list[0]
    witness2 = latest_witness_list[0]

    witness1_id = witness1.id
    witness2_id = witness2.id

    latest_partition_list1 = WitnessPartition.objects.filter(witness_id=witness1_id).order_by('char_start')
    latest_partition_list2 = WitnessPartition.objects.filter(witness_id=witness2_id).order_by('char_start')

    mrp1 = latest_partition_list1[0]
    mrp2 = latest_partition_list2[0]

    latest_annotations_list1 = Annotation.objects.filter(witness_id=witness1_id).order_by('char_start')
    latest_annotations_list2 = Annotation.objects.filter(witness_id=witness2_id).order_by('char_start')


    mrp1_id = mrp1.id
    mrp2_id = mrp2.id

    #latest_alignments_list = Alignment.objects.order_by('id')
    #latest_alignments_list = Alignment.objects.order_by('char_start_src')
    latest_alignments_list = Alignment.objects.filter(witness_src_id=witness1_id).filter(witness_dst_id=witness2_id).order_by('char_start_src')

    partition_array =[]

    go_a1 = latest_partition_list1[0]

    if len(latest_partition_list1) > 2:
        go_b1 = latest_partition_list1[1]
        go_c1 = latest_partition_list1[2]
        new_p1 = go_a1.content + go_b1.content + go_c1.content
        last_char1 = go_c1.char_end

    elif len(latest_partition_list1) > 1:
        go_b1 = latest_partition_list1[1]
        new_p1 = go_a1.content + go_b1.content
        last_char1 = go_b1.char_end

    else:
        new_p1 = go_a1.content
        last_char1 = go_a1.char_end

    go_a2 = latest_partition_list2[0]

    if len(latest_partition_list2) > 2:
        go_b2 = latest_partition_list2[1]
        go_c2 = latest_partition_list2[2]
        new_p2 = go_a2.content + go_b2.content + go_c2.content
        last_char2 = go_c2.char_end

    elif len(latest_partition_list2) > 1:
        go_b2 = latest_partition_list2[1]
        new_p2 = go_a2.content + go_b2.content
        last_char2 = go_b2.char_end

    else:
        new_p2 = go_a2.content
        last_char2 = go_a2.char_end

    partition_array.append(new_p1)
    partition_array.append(new_p2)

    json_partition = json.dumps(partition_array)

    first_char1 = go_a1.char_start
    first_char2 = go_a2.char_start

    from1 = 0
    to1 = 0
    from2 = 0
    to2 = 0

    lastselection1_start = 0;
    lastselection1_end = 0;
    lastselection2_start = 0;
    lastselection2_end = 0;

    # if no other information given, then set base witness
    # for 1 and 2 to first available witness by ID

    #usersettings.text1fg = '#FFFFFF'
    #usersettings.save()


    if request.POST:
        post = request.POST.copy()
        reallypost = post['reallypost']
        clickstatus = post['clickstatus']

        scrollvalue1 = post['scrollvalue1']
        scrollvalue2 = post['scrollvalue2']
        scrollvalue_alignments = post['scrollvalue_alignments']

        fg1 = post['fg1']
        bg1 = post['bg1']
        fg2 = post['fg2']
        bg2 = post['bg2']
        fg3 = post['fg3']
        bg3 = post['bg3']
        fg4 = post['fg4']
        bg4 = post['bg4']
        alignmentsfg = post['fgalignment']
        alignmentsbg = post['bgalignment']
        mainfg = post['fgmain']
        mainbg = post['bgmain']
        alignmentslistfg = post['fglist']
        alignmentslistbg = post['bglist']
        other1fg = post['other1fg']
        other1bg = post['other1bg']
        other2fg = post['other2fg']
        other2bg = post['other2bg']
        fontfamily = post['fontfamily']

        #current_user = request.user
        #usersettings = UserSettings.objects.filter(username_id=current_user.id).order_by('username_id')[0]

        #one_entry = latest_alignments_list.get(id=alignment_id)
        #one_entry.score = revisedscore
        #one_entry.save()

        #one_entry.save()

        lastselection1_start = post['lastselection1_start'];        
        lastselection1_end = post['lastselection1_end'];
        lastselection2_start = post['lastselection2_start'];
        lastselection2_end = post['lastselection2_end'];

        try:
            witness1_id = int(post['witness1_id'])
        except ValueError:
            witness1_id = latest_witness_list[0].id

        try:
            witness2_id = int(post['witness2_id'])
        except ValueError:
            witness2_id = latest_witness_list[0].id

        witness1 = latest_witness_list.get(id=witness1_id)
        witness2 = latest_witness_list.get(id=witness2_id)

        latest_partition_list1 = WitnessPartition.objects.filter(witness_id=witness1_id).order_by('char_start')
        latest_partition_list2 = WitnessPartition.objects.filter(witness_id=witness2_id).order_by('char_start')

        #latest_alignments_list = Alignment.objects.filter(witness_src_id=witness1_id).order_by('char_start_src')
        latest_alignments_list = Alignment.objects.filter(witness_src_id=witness1_id).filter(witness_dst_id=witness2_id).order_by('char_start_src')

        latest_annotations_list1 = Annotation.objects.filter(witness_id=witness1_id).order_by('char_start')
        latest_annotations_list2 = Annotation.objects.filter(witness_id=witness2_id).order_by('char_start')


        mrp1 = latest_partition_list1[0]
        mrp2 = latest_partition_list2[0]

        try:
            partition1_id = int(post['partition1_id'])
        except ValueError:
            partition1_id = mrp1.id
        try:
            partition2_id = int(post['partition2_id'])
        except ValueError:
            partition2_id = mrp2.id

        mrp1_id = partition1_id
        mrp2_id = partition2_id

        from1 = post['from1']
        try:
            from1 = int(post['from1'])
        except ValueError:
            from1 = None
        try:
            to1 = int(post['to1'])
        except ValueError:
            to1 = None
        try:
            from2 = int(post['from2'])
        except ValueError:
            from2 = None

        to2 = post['to2']
        try:
            to2 = int(post['to2'])
        except ValueError:
            to2 = None

        try:
            sc = int(post['score'])
        except ValueError:
            sc = None

        partition_array =[]

        try:
            go_a1 = latest_partition_list1.get(id=mrp1_id)
        except WitnessPartition.DoesNotExist:
            go_a1 = None

        if go_a1 != None:
            if (go_a1.witness_id != witness1_id):
                go_a1 = latest_partition_list1[0]
        
            if clickstatus== "w1left":
                try:
                    go_a1 = latest_partition_list1.get(char_end=go_a1.char_start)
                except WitnessPartition.DoesNotExist:
                    pass
                mrp1_id = go_a1.id
                
            elif clickstatus== "w1right":
                try:
                    go_a1 = latest_partition_list1.get(char_start=go_a1.char_end)
                except WitnessPartition.DoesNotExist:
                    pass
                mrp1_id = go_a1.id
                
        else:
            go_a1 = latest_partition_list1[0]
        
        first_char1 = go_a1.char_start
        go_b1_start = go_a1.char_end

        try:
            go_b1 = latest_partition_list1.get(char_start=go_b1_start)
        except WitnessPartition.DoesNotExist:
            go_b1 = None

        if go_b1 != None:
            go_c1_start = go_b1.char_end
            try:
                go_c1 = latest_partition_list1.get(char_start=go_c1_start)
            except WitnessPartition.DoesNotExist:
                go_c1 = None
            
            if go_c1 != None:
                new_p1 = go_a1.content + go_b1.content + go_c1.content
                last_char1 = go_c1.char_end
            else:
                new_p1 = go_a1.content + go_b1.content
                last_char1 = go_b1.char_end
        
        else:
            new_p1 = go_a1.content
            last_char1 = go_a1.char_end
            
        ################################################
        try:
            go_a2 = latest_partition_list2.get(id=mrp2_id)
        except WitnessPartition.DoesNotExist:
            go_a2 = None

        if go_a2 != None:
            if (go_a2.witness_id != witness2_id):
                go_a2 = latest_partition_list2[0]

            if clickstatus== "w2left":
                try:
                    go_a2 = latest_partition_list2.get(char_end=go_a2.char_start)
                except WitnessPartition.DoesNotExist:
                    pass
                mrp2_id = go_a2.id
                
            elif clickstatus== "w2right":
                try:
                    go_a2 = latest_partition_list2.get(char_start=go_a2.char_end)
                except WitnessPartition.DoesNotExist:
                    pass
                mrp2_id = go_a2.id
    
        else:
            go_a2 = latest_partition_list2[0]
            
        first_char2 = go_a2.char_start
        go_b2_start = go_a2.char_end

        try:
            go_b2 = latest_partition_list2.get(char_start=go_b2_start)
        except WitnessPartition.DoesNotExist:
            go_b2 = None

        if go_b2 != None:
            go_c2_start = go_b2.char_end
            try:
                go_c2 = latest_partition_list2.get(char_start=go_c2_start)
            except WitnessPartition.DoesNotExist:
                go_c2 = None
            
            if go_c2 != None:
                new_p2 = go_a2.content + go_b2.content + go_c2.content
                last_char2 = go_c2.char_end
            else:
                new_p2 = go_a2.content + go_b2.content
                last_char2 = go_b2.char_end
        
        else:
            new_p2 = go_a2.content
            last_char2 = go_a2.char_end
            
        ################################################
        ################################################
        
        partition_array.append(new_p1)
        partition_array.append(new_p2)

        mrp1 = latest_partition_list1.get(id=mrp1_id)
        mrp2 = latest_partition_list2.get(id=mrp2_id)

        json_partition = json.dumps(partition_array)

        if (from1 != None):
            cs_src=from1 + first_char1
        else:
            cs_src=from1

        if (to1 != None):
            ce_src=to1 + first_char1
        else:
            ce_src=to1

        if (from2 != None):
            cs_dst=from2 + first_char2
        else:
            cs_dst=from2

        if (to2 != None):
            ce_dst=to2 + first_char2
        else:
            ce_dst=to2

        t_id=2
        w_src_id=witness1_id
        w_dst_id=witness2_id
        
        if(reallypost == "1"):
            alignment = Alignment.objects.create(witness_src_id=w_src_id, witness_dst_id=w_dst_id, char_start_src=cs_src, char_end_src=ce_src, char_start_dst=cs_dst, char_end_dst=ce_dst, score=sc, type_id=t_id)
            alignment_log = AlignmentLog.objects.create(alignment_id=alignment.id, witness_src_id=w_src_id, witness_dst_id=w_dst_id, char_start_src=cs_src, char_end_src=ce_src, char_start_dst=cs_dst, char_end_dst=ce_dst, score=sc, type_id=t_id, user_id=5)
        # end create alignment, create log object

        if(reallypost == "2"):
            usersettings = UserSettings.objects.filter(username_id=current_user.id).order_by('username_id')[0]
            usersettings.text1fg = fg1
            usersettings.text1bg = bg1
            usersettings.text2fg = fg2
            usersettings.text2bg = bg2
            usersettings.text3fg = fg3
            usersettings.text3bg = bg3
            usersettings.text4fg = fg4
            usersettings.text4bg = bg4

            #usersettings.highlight1 = bg4
            #usersettings.highlight2 = bg4
            #usersettings.highlight3 = bg4
            #usersettings.highlight4 = bg4
            #usersettings.highlight5 = bg4

            usersettings.mainfg = mainfg
            usersettings.mainbg = mainbg

            usersettings.alignmentslistfg = alignmentslistfg
            usersettings.alignmentslistbg = alignmentslistbg
            usersettings.alignmentsfg = alignmentsfg
            usersettings.alignmentsbg = alignmentsbg
            usersettings.other1fg = other1fg
            usersettings.other1bg = other1bg
            usersettings.other2fg = other2fg
            usersettings.other2bg = other2bg

            usersettings.fontfamily = fontfamily

            usersettings.save()
        # end create alignment, create log object
    
    context = {
    'latest_witness_list': latest_witness_list,
    'latest_alignments_list': latest_alignments_list,
    'latest_partition_list1': latest_partition_list1,
    'latest_partition_list2': latest_partition_list2,
    'latest_annotations_list1': latest_annotations_list1,
    'latest_annotations_list2': latest_annotations_list2,
    'most_recent_witness1': witness1,
    'most_recent_witness2': witness2,
    'most_recent_partition1': mrp1_id,
    'most_recent_partition2': mrp2_id,
    'partition_array': json_partition,
    'first_char1': first_char1,
    'last_char1': last_char1,
    'first_char2': first_char2,
    'last_char2': last_char2,
    'lastselection1_start': lastselection1_start,
    'lastselection1_end': lastselection1_end,
    'lastselection2_start': lastselection2_start,
    'lastselection2_end': lastselection2_end,
    'scrollvalue1': scrollvalue1,
    'scrollvalue2': scrollvalue2,
    'scrollvalue_alignments': scrollvalue_alignments,
    'usersettings': usersettings,
     }

    return HttpResponse(template.render(context, request))

