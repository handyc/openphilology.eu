from django.http import HttpResponseRedirect, HttpResponseServerError
from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse

import json

from .models import Note
from editor.models import Work
from editor.models import WorkInCollection
from editor.models import Witness
from editor.models import WitnessPartition
from editor.models import Alignment
from editor.models import AlignmentLog
from editor.models import Annotation
from editor.models import AnnotationLog

template_location = 'optools/main.html'
dtemplate_location = 'optools/dictchk.html'

def dict_chk(request):
   
    error_msg = "error";
    template = loader.get_template(dtemplate_location)

    scrollvalue1 = "0"
    scrollvalue2 = "0"

    latest_witness_list = Witness.objects.order_by('id')
    latest_alignments_list = Alignment.objects.order_by('char_start_src')

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
    #one_entry = latest_alignments_list.get(id=alignment_id)

    #one_entry.score = revisedscore
    #one_entry.save()

    # new_log_entry =
    ### ADD NEW LOG ENTRY TO RECORD CHANGE
    #alignment = Alignment.objects.create(witness_src_id=w_src_id, witness_dst_id=w_dst_id, char_start_src=cs_src, char_end_src=ce_src, char_start_dst=cs_dst, char_end_dst=ce_dst, score=sc, type_id=t_id)
    
    #alignment_log = AlignmentLog.objects.create(alignment_id=alignment.id, witness_src_id=w_src_id, witness_dst_id=w_dst_id, char_start_src=cs_src, char_end_src=ce_src, char_start_dst=cs_dst, char_end_dst=ce_dst, score=sc, type_id=t_id, user_id=5)

    latest_alignments_list = Alignment.objects.order_by('char_start_src')


    """
    """

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
     }
    return HttpResponse(template.render(context, request))


def update_alignment(request):
   
    error_msg = "error";
    template = loader.get_template(template_location)

    scrollvalue1 = "0"
    scrollvalue2 = "0"

    latest_witness_list = Witness.objects.order_by('id')
    latest_alignments_list = Alignment.objects.order_by('char_start_src')

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
    one_entry = latest_alignments_list.get(id=alignment_id)

    one_entry.score = revisedscore
    one_entry.save()

    # new_log_entry =
    ### ADD NEW LOG ENTRY TO RECORD CHANGE
    #alignment = Alignment.objects.create(witness_src_id=w_src_id, witness_dst_id=w_dst_id, char_start_src=cs_src, char_end_src=ce_src, char_start_dst=cs_dst, char_end_dst=ce_dst, score=sc, type_id=t_id)
    
    #alignment_log = AlignmentLog.objects.create(alignment_id=alignment.id, witness_src_id=w_src_id, witness_dst_id=w_dst_id, char_start_src=cs_src, char_end_src=ce_src, char_start_dst=cs_dst, char_end_dst=ce_dst, score=sc, type_id=t_id, user_id=5)

    latest_alignments_list = Alignment.objects.order_by('char_start_src')


    """
    """

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
     }
    return HttpResponse(template.render(context, request))

def create_alignment(request):
    error_msg = "error";
    template = loader.get_template(template_location)

    scrollvalue1 = "0"
    scrollvalue2 = "0"

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
    latest_alignments_list = Alignment.objects.order_by('char_start_src')

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
     }

    return HttpResponse(template.render(context, request))
