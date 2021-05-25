from collections import OrderedDict
import xml.dom.minidom
from lxml import etree
from lxml.etree import QName

_DIGITAL_STR = 'digital'
_TITLE_STR = 'title'
_IMPLEMENTATION_STR = 'implementation'
_CHILD_STR = 'child'
_EXIT_STR = 'exit'
_SEMANTIC_STR = 'semantic'
_DEFINITIONS_STR = 'definitions'
_TIMER_STR = 'Timer'
_MIN_STR = 'min'
_MAX_STR = 'max'
_NUM_ID_SUFFIX = 'num_id'
_PREV_CHILD_SUFFIX = f'previous_{_CHILD_STR}'
_LIFELINE = 0  # is used for the correct alignment of substeps and their substeps

_MAX_DURATION_TEMPLATE = {
    'Λεπτά': 'PT{}M',
    'Ώρες': 'PT{}Η',
    'Ημέρες': 'P{}DS',
    'Εβδομάδες': 'P{}WS',
    'Μήνες': 'P{}MS'
}

"""
adds extra brackets to a json string
"""
def bracketize(string):
    return f'{{{string}}}'

"""
converts the total duration for all steps to string
"""
def get_max_duration_as_string(timer):
    duration_type = timer[2]
    try:
        template = _MAX_DURATION_TEMPLATE[duration_type]
    except KeyError:
        return ''
    max_duration = timer[1]
    min_duration = timer[0]
    out = max(float(max_duration), float(min_duration))
    return template.format(out)


class BPMNNamespaces:
    def __init__(self, semantic, bpmndi, di, dc, xsi, nsmap, di_namespace, xsi_namespace):
        self.semantic = semantic
        self.bpmndi = bpmndi
        self.di = di
        self.dc = dc
        self.xsi = xsi
        self.NSMAP = nsmap
        self.di_NAMESPACE = di_namespace
        self.xsi_NAMESPACE = xsi_namespace


class BPMN:
    _columnWidth = 60
    _rowHeight = 100
    _branches = {}
    # Keys
    _SEMANTIC_KEY = _SEMANTIC_STR
    _DEFINITIONS_KEY = _DEFINITIONS_STR
    _BPMNDI_KEY = 'bpmndi'
    _DI_KEY = 'di'
    _DC_KEY = 'dc'
    _XSI_KEY = 'xsi'
    _XML_TARGET_KEY = 'xml_target'
    _PROCESS_EVIDENCE_DESCR_KEY = 'process_evidence_description'
    _NAME_KEY = 'name'
    _DOCUMENTATION_KEY = 'documentation'
    _RESOLUTION_KEY = 'resolution'
    _TYPE_KEY = 'type'
    _FIELDS_KEY = 'fields'
    _WIDTH_KEY = 'width'
    _HEIGHT_KEY = 'height'
    _STEP_NUM_ID='process_step_num_id'
    _STEP_NUM_ID_DIGITAL = 'process_step_digital_num_id'
    # Prefixes
    _SEQUENCE_FLOW_PREFIX = 'SequenceFlow_'
    _START_EVENT_PREFIX = 'StartEvent_'
    _END_EVENT_PREFIX = 'EndEvent_'
    _PR_PREFIX = 'pr_'
    _TASK_PREFIX = 'Task_'
    _SUBTASK_PREFIX = 'Subtask_'
    _PARTICIPANT_PREFIX = 'participant_'
    _EXCLUSIVE_GATEWAY_PREFIX = 'ExclusiveGateway_'
    _C_PREFIX = 'C'
    _TIMER_PREFIX = f'{_TIMER_STR}_'
    # Suffixes
    _WAYPOINT_SUFFIX = 'waypoint'
    _START_EVENT_SUFFIX = 'startEvent'
    _OUTGOING_SUFFIX = 'outgoing'
    _SEQUENCE_FLOW_SUFFIX = 'sequenceFlow'
    _END_EVENT_SUFFIX = 'endEvent'
    _DATA_OBJECT_SUFFIX = 'dataObject'
    _DATA_OBJECT_REFERENCE_SUFFIX = 'dataObjectReference'
    _DATA_OBJECT_PREFIX = 'DataObject_'
    _DATA_OBJECT_REFERENCE_PREFIX = 'DataObjectReference_'
    _INCOMING_SUFFIX = 'incoming'
    _TASK_SUFFIX = 'task'
    _MANUAL_TASK_SUFFIX = 'manualTask'
    _SERVICE_TASK_SUFFIX = 'serviceTask'
    _COLLABORATION_SUFFIX = 'collaboration'
    _PARTICIPANT_SUFFIX = 'participant'
    _EXCLUSIVE_GATEWAY_SUFFIX = 'exclusiveGateway'
    _1_SUFFIX = '_1'
    _LAST_SUFFIX = '_last'
    _DI_SUFFIX = '_di'
    _1_DI_SUFFIX = '_1_di'
    _LAST_DI_SUFFIX = '_last_di'
    _BOUNDS_SUFFIX = 'Bounds'
    _SHAPE_SUFFIX = 'BPMNShape'
    _LABEL_SUFFIX = 'BPMNLabel'
    _EDGE_SUFFIX = 'BPMNEdge'
    _DIAGRAM_SUFFIX = 'BPMNDiagram'
    _PLANE_SUFFIX = 'BPMNPlane'
    _BOUNDARY_EVENT_SUFFIX = 'boundaryEvent'
    _TIMER_EVENT_DEF_SUFFIX = 'timerEventDefinition'
    _TIME_DURATION_SUFFIX = 'timeDuration'
    # Process evidences
    _PROCESS_EVIDENCES_STR = 'Process evidences'
    _PROCESS_EVIDENCE_PREFIX = 'process_evidence'
    # Process steps
    _PROCESS_STEPS_STR = 'Process steps'
    _PROCESS_STEPS_DIGITAL_STR = 'Process steps digital'
    _PROCESS_STEP_PREFIX = 'process_step'
    _PROCESS_STEP_TITLE = None
    _PROCESS_STEP_IMPLEMENTATION = None
    _PROCESS_STEP_CHILD = None
    _PROCESS_STEP_EXIT = None
    _PROCESS_STEP_PREVIOUS_CHILD = None

    # Process steps duration
    _PROCESS_STEP_DURATION_MAX = 'process_step_duration_max'
    _PROCESS_STEP_DURATION_MIN = 'process_step_duration_min'
    _PROCESS_STEP_DURATION_TYPE = 'process_step_duration_type'
    _PROCESS_STEP_DIGITAL_DURATION_MAX = 'process_step_digital_duration_max'
    _PROCESS_STEP_DIGITAL_DURATION_MIN = 'process_step_digital_duration_min'
    _PROCESS_STEP_DIGITAL_DURATION_TYPE = 'process_step_digital_duration_type'
    _TFORMALEXPRESSION = 'tFormalExpression'

    # X
    _X_SHAPE = 100
    # Y
    _Y_SHAPE = 218
    _Y_SHAPE_VARIANT = 221
    _Y_SHAPE_VARIANT_2 = 257
    _Y_SHAPE_VARIANT_3 = 111
    _Y_LABEL = 230
    _Y_LABEL_VARIANT = 190
    _Y_START = 240
    # Widths
    _WIDTH_TASK = 100
    _WIDTH_ARROW = 50
    _WIDTH_RHOMBUS = 50
    _WIDTH_START_EVENT = 36
    _WIDTH_LABEL = 90
    _WIDTH_LABEL_VARIANT = 30
    _WIDTH_LABEL_VARIANT_2 = 190
    _WIDTH_DOC_ICON = 36
    # Heights
    _HEIGHT_LABEL = 40
    _HEIGHT_LABEL_VARIANT = _WIDTH_LABEL_VARIANT
    _HEIGHT_RHOMBUS = _WIDTH_RHOMBUS
    _HEIGHT_DOC_ICON = 50
    # Offsets
    _OFFSET_BOUNDS = 15
    _OFFSET_X_LABEL = 19
    _OFFSET_Y_LABEL = 10
    _OFFSET_HANDLE_PLAIN_NODE_SHAPES = 50
    _OFFSET_X_APPEND_SHAPES_AND_EDGES = 150
    _OFFSET_DOC_TAB = 140
    _OFFSET_X_DOC = 100
    _OFFSET_Y_DOC = 150
    _OFFSET_EVIDENCES_Y_LABEL = 70
    _OFFSET_BOUNDS_WIDTH = 0
    # Multipliers
    _MULTIPLIER_BOX_HEIGHT = 120
    _MULTIPLIER_TASK_TEXT_HEIGHT = 27
    _MULTIPLIER_EVIDENCES_TEXT_HEIGHT = 10
    # Divisors
    _DIVISOR_BOX_HEIGHT = 25
    _DIVISOR_TASK_ROWS = 10
    _DIVISOR_EVIDENCES_ROWS = 6.5
    # Iraklis stuff
    # Widths
    _TASK_WIDTH = 100
    _ARROW_WIDTH = 50
    _RHOMBUS_WIDTH = 50
    _START_EVENT_WIDTH = 36
    # HEIGHTS
    _CHAINS_y_OFFSET = 120
    # Namespaces
    _NAMESPACE = {
        _SEMANTIC_KEY: 'http://www.omg.org/spec/BPMN/20100524/MODEL',
        _BPMNDI_KEY: 'http://www.omg.org/spec/BPMN/20100524/DI',
        _DI_KEY: 'http://www.omg.org/spec/DD/20100524/DI',
        _DC_KEY: 'http://www.omg.org/spec/DD/20100524/DC',
        _XSI_KEY: 'http://www.w3.org/2001/XMLSchema-instance',
        _XML_TARGET_KEY: 'http://www.trisotech.com/definitions/_1276276944297'
    }
    # Attributes
    _NAME_ATTR_PREFIX = 'Collaboration Diagram for '
    _DOCUMENTATION_ATTR = ''
    _RESOLUTION_ATTR = '96.00000267028808'
    _TYPE_ATTR = 'dc:Point'
    # Other
    _SEQUENCE_FLOW_0 = 'SequenceFlow_0'
    _START_EVENT_0 = 'StartEvent_0'
    _START_EVENT_NAME = 'Έναρξη'
    _END_EVENT_NAME = 'Λήξη'
    _SELECTION_NAME = 'Επιλογή'
    _MANUAL_TASK = 'Χειροκίνητη ενέργεια'
    _SERVICE_TASK = 'Ενέργεια μέσω λογισμικού'
    _TASK_1_NAME = 'Task_1'
    _PROCESS_STR = 'process'
    _LANE_SET_STR = 'laneSet'
    _IS_EXECUTABLE_FALSE = 'false'
    _IS_MARKER_VISIBLE_TRUE = 'true'
    _IS_HORIZONTAL_TRUE = 'true'
    _PROCESS_STEP_CHILD_YES = 'Ναι'
    _PROCESS_STEP_EXIT_YES = 'Ναι'
    _TRISOTECH_ID = 'Trisotech.Visio_'
    _TRISOTECH_ID_6 = 'Trisotech.Visio-_6'
    _PLANE_FIND_ALL_QUERY = './bpmndi:BPMNShape[@isHorizontal]/dc:Bounds'

    def __init__(self, digital_steps=False):
        if digital_steps:
            self._PROCESS_STEPS_STR += f' {_DIGITAL_STR}'
            process_step_prefix = f'{self._PROCESS_STEP_PREFIX}_{_DIGITAL_STR}'
        else:
            process_step_prefix = self._PROCESS_STEP_PREFIX
        self._PROCESS_STEP_TITLE = f'{process_step_prefix}_{_TITLE_STR}'
        self._PROCESS_STEP_IMPLEMENTATION = f'{process_step_prefix}_{_IMPLEMENTATION_STR}'
        self._PROCESS_STEP_NUM_ID = f'{process_step_prefix}_{_NUM_ID_SUFFIX}'
        self._PROCESS_STEP_CHILD = f'{process_step_prefix}_{_CHILD_STR}'
        self._PROCESS_STEP_EXIT = f'{process_step_prefix}_{_EXIT_STR}'
        self._PROCESS_STEP_PREVIOUS_CHILD = f'{process_step_prefix}_' \
                                            f'{_PREV_CHILD_SUFFIX}'

        self._ns = BPMNNamespaces(
            semantic=bracketize(self._NAMESPACE[self._SEMANTIC_KEY]),
            bpmndi=bracketize(self._NAMESPACE[self._BPMNDI_KEY]),
            di=bracketize(self._NAMESPACE[self._DI_KEY]),
            dc=bracketize(self._NAMESPACE[self._DC_KEY]),
            xsi=bracketize(self._NAMESPACE[self._XSI_KEY]),
            nsmap=self._NAMESPACE,
            di_namespace=self._NAMESPACE[self._DI_KEY],
            xsi_namespace=self._NAMESPACE[self._XSI_KEY])
        self._process_steps = None
        self._process_evidences = None

    def group_options(self, opts):
        exit_nodes=[]
        chains = {}
        forward_chains = {}
        for opt in opts:
            curr = opt.get(self._PROCESS_STEP_NUM_ID)
            prev = opt.get(self._PROCESS_STEP_PREVIOUS_CHILD)
            if opt.get(self._PROCESS_STEP_EXIT) == self._PROCESS_STEP_EXIT_YES:
                exit_nodes.append(curr)
            if chains.get(prev) is not None:
                arr = chains.get(prev)
                arr.append(opt)
                chains.pop(prev, None)
                chains[curr] = arr
                tup = (prev, curr)
                if prev in forward_chains.keys():
                    tups = forward_chains[prev]
                    tups.append(tup)
                    forward_chains[prev] = tups
                else:
                    tups = []
                    tups.append(tup)
                    forward_chains[prev] = tups
            else:
                arr = []
                arr.append(opt)
                chains[curr] = arr
                tup = (prev, curr)
                if prev in forward_chains.keys():
                    tups = forward_chains[prev]
                    tups.append(tup)
                    forward_chains[prev] = tups
                else:
                    tups = []
                    tups.append(tup)
                    forward_chains[prev] = tups
        max_chain_length = 0
        for k in chains:
            if len(chains.get(k)) > max_chain_length:
                max_chain_length = len(chains.get(k))
        return chains, max_chain_length, forward_chains, exit_nodes

    def _create_waypoint(self, bpmn_edge, xpos, ypos):
        waypoint = etree.SubElement(
            bpmn_edge,
            self._ns.di + self._WAYPOINT_SUFFIX,
            x=str(xpos),
            y=str(ypos),
            nsmap=self._ns.NSMAP)
        return waypoint

    def _append_start_event_tree(self, process, allnodes):
        """Append the xml elements of the StartEvent"""
        task = etree.SubElement(
            process, self._ns.semantic + self._START_EVENT_SUFFIX,
            id=self._START_EVENT_0,
            name=self._START_EVENT_NAME, nsmap=self._ns.NSMAP)
        outgoing = etree.SubElement(
            task, self._ns.semantic + self._OUTGOING_SUFFIX,
            nsmap=self._ns.NSMAP)
        outgoing.text = self._SEQUENCE_FLOW_0
        allnodes.append(self._START_EVENT_0)

    def _append_data_objects(self, process):
        stepcount = 0
        # Parse the Evidences and add a dataObject and a dataObjectReference
        # for each
        for _, evidence in self._process_evidences.items():
            stepcount += 1
            evid_name = evidence[self._PROCESS_EVIDENCE_DESCR_KEY]
            if evid_name is not None:
                if len(evid_name) > 120:
                    evid_name = evid_name[:120] + '...'
                etree.SubElement(
                    process,
                    self._ns.semantic + self._DATA_OBJECT_SUFFIX,
                    id=self._DATA_OBJECT_PREFIX + str(stepcount))
                etree.SubElement(
                    process,
                    self._ns.semantic + self._DATA_OBJECT_REFERENCE_SUFFIX,
                    id=self._DATA_OBJECT_REFERENCE_PREFIX + str(stepcount),
                    name=evid_name,
                    dataObjectRef=self._DATA_OBJECT_PREFIX + str(stepcount))

    def _append_end_nodes(self, process, allnodes, stepcount):
        """Append the xml elements of the EndEvent"""
        stepname = self._END_EVENT_NAME
        task = etree.SubElement(process,
                                self._ns.semantic + self._END_EVENT_SUFFIX,
                                id=self._END_EVENT_PREFIX + str(stepcount + 1),
                                name=stepname, nsmap=self._ns.NSMAP)
        incoming = etree.SubElement(
            task, self._ns.semantic + self._INCOMING_SUFFIX,
            nsmap=self._ns.NSMAP)
        incoming.text = self._SEQUENCE_FLOW_PREFIX + str(stepcount)
        allnodes.append(self._END_EVENT_PREFIX + str(stepcount + 1))
        task = etree.SubElement(
            process, self._ns.semantic + self._SEQUENCE_FLOW_SUFFIX,
            id=(self._SEQUENCE_FLOW_PREFIX + str(stepcount)),
            sourceRef=allnodes[stepcount],
            targetRef=allnodes[stepcount + 1],
            nsmap=self._ns.NSMAP)



    def _append_multiple_end_nodes(self, process, options):
        if len(options)>1:
            # add the ExclusiveGateway
            suffix=''
            for opt in options:
                to_node =opt.get(self._PROCESS_STEP_NUM_ID)
                opt.get(self._PROCESS_STEP_PREVIOUS_CHILD)
                suffix = suffix + to_node + '.'

            _, _, forwardchains, _ = self.group_options(options)
            self._add_branch_nodes(options, process, forwardchains)

    def _append_process_tree(self, definition, process_name):
        process = etree.SubElement(definition,
                                   self._ns.semantic + self._PROCESS_STR,
                                   id=self._PR_PREFIX + str(
                                       hash(process_name)),
                                   isExecutable=self._IS_EXECUTABLE_FALSE,
                                   nsmap=self._ns.NSMAP)
        etree.SubElement(process, self._ns.semantic + self._LANE_SET_STR,
                         nsmap=self._ns.NSMAP)
        stepcount = 0
        allnodes = []
        options = []
        branched = False
        # Add a default startEvent
        self._append_start_event_tree(process, allnodes)
        # Parse the process steps and either add plainEventNodes, or
        # put the branchNodes in a list and handle them when the first
        # plainEventNode appears
        for _, step in self._process_steps.items():
            stepcount += 1
            if step.get(self._PROCESS_STEP_TITLE) is not None:
                if step.get(self._PROCESS_STEP_CHILD) == \
                        self._PROCESS_STEP_CHILD_YES:
                    options.append(step)
                    allnodes.append(self._TASK_PREFIX + str(stepcount))
                    branched = True
                else:
                    self._handle_plain_nodes(process, options, stepcount)
                    allnodes.append(self._TASK_PREFIX + str(stepcount))
                    options = []
                    if not branched:
                        etree.SubElement(
                            process,
                            self._ns.semantic + self._SEQUENCE_FLOW_SUFFIX,
                            id=self._SEQUENCE_FLOW_PREFIX + str(stepcount - 1),
                            sourceRef=allnodes[stepcount - 1],
                            targetRef=allnodes[stepcount],
                            nsmap=self._ns.NSMAP)
                    branched = False
        if len(options)>0:
            # Add multiple endEvents
            self._append_multiple_end_nodes(process, options)
        else:
            # Add a default endEvent
            self._append_end_nodes(process, allnodes, stepcount)
        return process

    def _handle_plain_nodes(self, process, options, stepcount):
        process_steps = self._process_steps
        stepname = process_steps[stepcount].get(self._PROCESS_STEP_TITLE)
        stepimpl = process_steps[stepcount].get(
            self._PROCESS_STEP_IMPLEMENTATION)
        if stepimpl == self._MANUAL_TASK:
            steptype = self._MANUAL_TASK_SUFFIX
        elif stepimpl == self._SERVICE_TASK:
            steptype = self._SERVICE_TASK_SUFFIX
        else:
            steptype = self._TASK_SUFFIX
        step = process_steps[stepcount]
        if self._PROCESS_STEPS_STR == self._PROCESS_STEPS_DIGITAL_STR:
            timer = (step.get(self._PROCESS_STEP_DIGITAL_DURATION_MIN),
                     step.get(self._PROCESS_STEP_DIGITAL_DURATION_MAX),
                     step.get(self._PROCESS_STEP_DIGITAL_DURATION_TYPE))
        else:
            timer = (step.get(self._PROCESS_STEP_DURATION_MIN),
                     step.get(self._PROCESS_STEP_DURATION_MAX),
                     step.get(self._PROCESS_STEP_DURATION_TYPE))

        # If no BranchNodes are found
        if len(options) == 0:
            task = etree.SubElement(process,
                                    self._ns.semantic + steptype,
                                    id=self._TASK_PREFIX + str(stepcount),
                                    name=stepname, nsmap=self._ns.NSMAP)
            name = f'{_MIN_STR}:{timer[0]}, {_MAX_STR}:{timer[1]} {timer[2]}'
            boundary_event = etree.SubElement(
                process, self._ns.semantic + self._BOUNDARY_EVENT_SUFFIX,
                id=self._TIMER_PREFIX + str(stepcount),
                # name=self._TASK_PREFIX + str(stepcount)+"_Duration",
                name=name,
                attachedToRef=self._TASK_PREFIX + str(stepcount),
                nsmap=self._ns.NSMAP)
            timer_event = etree.SubElement(
                boundary_event,
                self._ns.semantic + self._TIMER_EVENT_DEF_SUFFIX)
            time_duration = etree.SubElement(
                timer_event, self._ns.semantic + self._TIME_DURATION_SUFFIX)
            time_duration.attrib[
                QName(self._ns.xsi_NAMESPACE, self._TYPE_KEY)] = \
                _SEMANTIC_STR + ':' + self._TFORMALEXPRESSION
            time_duration.text = get_max_duration_as_string(timer)
            incoming = etree.SubElement(
                task, self._ns.semantic + self._INCOMING_SUFFIX,
                nsmap=self._ns.NSMAP)
            incoming.text = self._SEQUENCE_FLOW_PREFIX + str(stepcount - 1)
            outgoing = etree.SubElement(
                task, self._ns.semantic + self._OUTGOING_SUFFIX,
                nsmap=self._ns.NSMAP)
            to_node=str(stepcount)
            outgoing.text = self._SEQUENCE_FLOW_PREFIX + to_node

            if step[self._PROCESS_STEP_EXIT] == self._PROCESS_STEP_EXIT_YES:
                self._add_end_node(process, to_node)
        # If there BranchNodes are found from the previous event
        else:
            _, _, forwardchains, _ = self.group_options(options)
            nodes_left_to_merge= self._add_branch_nodes(options, process, forwardchains)
            self._add_merge_nodes(process, stepcount, stepname, steptype, timer,
                                  nodes_left_to_merge)
            options = []

    def _append_collaboration(self, definition, process_name):
        collaboration = etree.SubElement(
            definition,
            self._ns.semantic + self._COLLABORATION_SUFFIX,
            id=self._C_PREFIX + str(hash(process_name)),
            nsmap=self._ns.NSMAP)
        etree.SubElement(
            collaboration, self._ns.semantic + self._PARTICIPANT_SUFFIX,
            id=self._PARTICIPANT_PREFIX + str(hash(process_name)),
            name=process_name,
            processRef=self._PR_PREFIX + str(hash(process_name)),
            nsmap=self._ns.NSMAP)


    def _add_branch_nodes(self, options, process, forwardchains):
        # Add an exclusiveGateway node, with an incoming edge
        nodes_left_to_merge=[]
        optionsdict={}
        if self._PROCESS_STEPS_STR == self._PROCESS_STEPS_DIGITAL_STR:
            step_num_id = self._STEP_NUM_ID_DIGITAL
        else:
            step_num_id = self._STEP_NUM_ID
        for opt in options:
            optionsdict[opt[step_num_id]]=opt

        splits=[]
        for k in forwardchains.keys():
            if len(forwardchains[k])>1:
                splits.append(k)
                suffix=''
                for from_node, to_node in forwardchains[k]:
                    suffix=suffix+to_node+'.'

                exclusive_gateway = etree.SubElement(
                    process, self._ns.semantic + self._EXCLUSIVE_GATEWAY_SUFFIX,
                    # id=self._EXCLUSIVE_GATEWAY_PREFIX + str(stepcount - len(options)),
                    id=self._EXCLUSIVE_GATEWAY_PREFIX + str(k) + '_' + suffix[:-1],
                    name=self._SELECTION_NAME, nsmap=self._ns.NSMAP)
                incoming = etree.SubElement(
                    exclusive_gateway,
                    self._ns.semantic + self._INCOMING_SUFFIX,
                    nsmap=self._ns.NSMAP)
                incoming.text = self._SEQUENCE_FLOW_PREFIX + str(k) #+'_EG'+str(k)

                for from_node, to_node in forwardchains[k]:
                    outgoing = etree.SubElement(exclusive_gateway, self._ns.semantic
                                                + self._OUTGOING_SUFFIX, nsmap=self._ns.NSMAP)
                    # ii)  e.g. SequenceFlow_3_1_1, SequenceFlow_3_2_1  etc.
                    outgoing.text = self._SEQUENCE_FLOW_PREFIX + from_node + '.' + to_node

                # Add a sequenceFlow for the exclusiveGateway's incoming edge

                etree.SubElement(
                    process, self._ns.semantic + self._SEQUENCE_FLOW_SUFFIX,
                    id=self._SEQUENCE_FLOW_PREFIX + str(k),
                    sourceRef=self._TASK_PREFIX+str(k),
                    targetRef=self._EXCLUSIVE_GATEWAY_PREFIX + str(k) + '_' + suffix[:-1],
                    nsmap=self._ns.NSMAP)
                for from_node, to_node in forwardchains[k]:
                    step=optionsdict[to_node]
                    stepimpl = step.get(self._PROCESS_STEP_IMPLEMENTATION)
                    if stepimpl == self._MANUAL_TASK:
                        steptype = self._MANUAL_TASK_SUFFIX
                    elif stepimpl == self._SERVICE_TASK:
                        steptype = self._SERVICE_TASK_SUFFIX
                    else:
                        steptype = self._TASK_SUFFIX

                    if self._PROCESS_STEPS_STR == self._PROCESS_STEPS_DIGITAL_STR:
                        timer = (step.get(self._PROCESS_STEP_DIGITAL_DURATION_MIN),
                                 step.get(self._PROCESS_STEP_DIGITAL_DURATION_MAX),
                                 step.get(self._PROCESS_STEP_DIGITAL_DURATION_TYPE))
                    else:
                        timer = (step.get(self._PROCESS_STEP_DURATION_MIN),
                                 step.get(self._PROCESS_STEP_DURATION_MAX),
                                 step.get(self._PROCESS_STEP_DURATION_TYPE))
                    sub_task = etree.SubElement(
                        process, self._ns.semantic + steptype,
                        id=self._TASK_PREFIX + to_node,
                        name=step.get(self._PROCESS_STEP_TITLE),
                        nsmap=self._ns.NSMAP)
                    name = f'{_MIN_STR}:{timer[0]}, {_MAX_STR}:{timer[1]} {timer[2]}'
                    boundary_event = etree.SubElement(
                        process, self._ns.semantic + self._BOUNDARY_EVENT_SUFFIX,
                        id=self._TIMER_PREFIX + to_node,
                        name=name,
                        attachedToRef=self._TASK_PREFIX + to_node,
                        nsmap=self._ns.NSMAP)
                    timer_event = etree.SubElement(
                        boundary_event,
                        self._ns.semantic + self._TIMER_EVENT_DEF_SUFFIX)
                    time_duration = etree.SubElement(
                        timer_event, self._ns.semantic + self._TIME_DURATION_SUFFIX)
                    time_duration.attrib[
                        QName(self._ns.xsi_NAMESPACE, self._TYPE_KEY)] = \
                        _SEMANTIC_STR + ':' + self._TFORMALEXPRESSION
                    time_duration.text = get_max_duration_as_string(timer)
                    # Set the current task as the last task of the chain
                    incoming = etree.SubElement(
                        sub_task, self._ns.semantic + self._INCOMING_SUFFIX,
                        nsmap=self._ns.NSMAP)
                    incoming.text = self._SEQUENCE_FLOW_PREFIX + from_node + '.' + to_node
                    etree.SubElement(
                        process,
                        self._ns.semantic + self._SEQUENCE_FLOW_SUFFIX,
                        id=self._SEQUENCE_FLOW_PREFIX + from_node + '.' + to_node,
                        sourceRef=self._EXCLUSIVE_GATEWAY_PREFIX + str(k) + '_' + suffix[:-1],
                        targetRef = self._TASK_PREFIX + to_node, nsmap = self._ns.NSMAP)

                    if to_node in forwardchains.keys():
                        if len(forwardchains[to_node])>1:
                            strsuffix = ''
                        else:
                            _,next_node=forwardchains[to_node][0]
                            strsuffix = '.'+next_node
                    else:
                        strsuffix='_out'
                        nodes_left_to_merge.append(optionsdict[to_node])

                    if step[self._PROCESS_STEP_EXIT] == self._PROCESS_STEP_EXIT_YES:
                        self._add_end_node(process,to_node)

                    outgoing = etree.SubElement(sub_task, self._ns.semantic
                                                + self._OUTGOING_SUFFIX, nsmap=self._ns.NSMAP)
                    outgoing.text = self._SEQUENCE_FLOW_PREFIX + to_node+strsuffix
            else:
                from_node, to_node = forwardchains[k][0]
                step = optionsdict[to_node]
                stepimpl = step.get(self._PROCESS_STEP_IMPLEMENTATION)
                if stepimpl == self._MANUAL_TASK:
                    steptype = self._MANUAL_TASK_SUFFIX
                elif stepimpl == self._SERVICE_TASK:
                    steptype = self._SERVICE_TASK_SUFFIX
                else:
                    steptype = self._TASK_SUFFIX

                if self._PROCESS_STEPS_STR == self._PROCESS_STEPS_DIGITAL_STR:
                    timer = (step.get(self._PROCESS_STEP_DIGITAL_DURATION_MIN),
                             step.get(self._PROCESS_STEP_DIGITAL_DURATION_MAX),
                             step.get(self._PROCESS_STEP_DIGITAL_DURATION_TYPE))
                else:
                    timer = (step.get(self._PROCESS_STEP_DURATION_MIN),
                             step.get(self._PROCESS_STEP_DURATION_MAX),
                             step.get(self._PROCESS_STEP_DURATION_TYPE))
                sub_task = etree.SubElement(
                    process, self._ns.semantic + steptype,
                    id=self._TASK_PREFIX + to_node,
                    name=step.get(self._PROCESS_STEP_TITLE),
                    nsmap=self._ns.NSMAP)
                name = f'{_MIN_STR}:{timer[0]}, {_MAX_STR}:{timer[1]} {timer[2]}'
                boundary_event = etree.SubElement(
                    process, self._ns.semantic + self._BOUNDARY_EVENT_SUFFIX,
                    id=self._TIMER_PREFIX + to_node,
                    name=name,
                    attachedToRef=self._TASK_PREFIX + to_node,
                    nsmap=self._ns.NSMAP)
                timer_event = etree.SubElement(
                    boundary_event,
                    self._ns.semantic + self._TIMER_EVENT_DEF_SUFFIX)
                time_duration = etree.SubElement(
                    timer_event, self._ns.semantic + self._TIME_DURATION_SUFFIX)
                time_duration.attrib[QName(self._ns.xsi_NAMESPACE, self._TYPE_KEY)] \
                    = _SEMANTIC_STR + ':' + self._TFORMALEXPRESSION
                time_duration.text = get_max_duration_as_string(timer)
                # Set the current task as the last task of the chain
                incoming = etree.SubElement(
                    sub_task, self._ns.semantic + self._INCOMING_SUFFIX,
                    nsmap=self._ns.NSMAP)
                incoming.text = self._SEQUENCE_FLOW_PREFIX + from_node + '.' + to_node
                etree.SubElement(
                    process,
                    self._ns.semantic + self._SEQUENCE_FLOW_SUFFIX,
                    id=self._SEQUENCE_FLOW_PREFIX + from_node + '.' + to_node,
                    sourceRef=self._TASK_PREFIX + from_node,
                    targetRef=self._TASK_PREFIX + to_node, nsmap=self._ns.NSMAP)

                if to_node in forwardchains.keys():
                    if len(forwardchains[to_node]) > 1:
                        strsuffix = ''
                    else:
                        strsuffix = '.' + forwardchains[to_node][0][1]
                else:
                    strsuffix = '_out'

                if step[self._PROCESS_STEP_EXIT] == self._PROCESS_STEP_EXIT_YES:
                    self._add_end_node(process,to_node)
                else:
                    nodes_left_to_merge.append(optionsdict[to_node])

                outgoing = etree.SubElement(sub_task, self._ns.semantic
                                            + self._OUTGOING_SUFFIX, nsmap=self._ns.NSMAP)
                outgoing.text = self._SEQUENCE_FLOW_PREFIX + to_node + strsuffix

        # Add:
        # i) the outgoing edges
        # ii) the sequenceFlows for the outgoing edges,
        # iii) the subtasks,
        # iv) their incoming and outgoing edges,
        # v) the respective SequenceFlows for these edges
        return nodes_left_to_merge


    def _add_end_node(self, process, to_node):
        task = etree.SubElement(process,
                                self._ns.semantic + self._END_EVENT_SUFFIX,
                                # id=self._END_EVENT_PREFIX + str(stepcount + 1),
                                id=self._END_EVENT_PREFIX + to_node + '_end',
                                name=self._END_EVENT_NAME, nsmap=self._ns.NSMAP)
        incoming = etree.SubElement(
            task, self._ns.semantic + self._INCOMING_SUFFIX,
            nsmap=self._ns.NSMAP)
        incoming.text = self._SEQUENCE_FLOW_PREFIX + to_node + '_out'
        etree.SubElement(
            process,
            self._ns.semantic + self._SEQUENCE_FLOW_SUFFIX,
            id=self._SEQUENCE_FLOW_PREFIX + to_node + '_out',
            # sourceRef=self._EXCLUSIVE_GATEWAY_PREFIX + str(k) + '_' + suffix[:-1],
            sourceRef=self._TASK_PREFIX + to_node,
            targetRef=self._END_EVENT_PREFIX + to_node + '_end', nsmap=self._ns.NSMAP)

    def _add_merge_nodes(self, process, stepcount,
                       stepname, steptype, timer, nodes_left_to_merge):
        task = etree.SubElement(process, self._ns.semantic + steptype,
                                id=self._TASK_PREFIX + str(stepcount),
                                name=stepname, nsmap=self._ns.NSMAP)
        outgoing = etree.SubElement(
            task, self._ns.semantic + self._OUTGOING_SUFFIX,
            nsmap=self._ns.NSMAP)
        outgoing.text = self._SEQUENCE_FLOW_PREFIX + str(stepcount)
        name = f'{_MIN_STR}:{timer[0]}, {_MAX_STR}:{timer[1]} {timer[2]}'
        boundary_event = etree.SubElement(
            process, self._ns.semantic + self._BOUNDARY_EVENT_SUFFIX,
            id=self._TIMER_PREFIX + str(stepcount),
            name=name,
            attachedToRef=self._TASK_PREFIX + str(stepcount),
            nsmap=self._ns.NSMAP)
        timer_event = etree.SubElement(
            boundary_event, self._ns.semantic + self._TIMER_EVENT_DEF_SUFFIX)
        time_duration = etree.SubElement(
            timer_event, self._ns.semantic + self._TIME_DURATION_SUFFIX)
        time_duration.attrib[
            QName(self._ns.xsi_NAMESPACE, self._TYPE_KEY)] = \
            _SEMANTIC_STR + ':' + self._TFORMALEXPRESSION
        time_duration.text = get_max_duration_as_string(timer)
        if self._PROCESS_STEPS_STR == self._PROCESS_STEPS_DIGITAL_STR:
            step_num_id = self._STEP_NUM_ID_DIGITAL
        else:
            step_num_id = self._STEP_NUM_ID
        for node in nodes_left_to_merge:
            if node.get(self._PROCESS_STEP_EXIT)==self._PROCESS_STEP_EXIT_YES:
                continue
            to_node=node[step_num_id]
            incoming = etree.SubElement(
                task, self._ns.semantic + self._INCOMING_SUFFIX,
                nsmap=self._ns.NSMAP)
            incoming.text = self._SEQUENCE_FLOW_PREFIX  +to_node+ '_out'
            etree.SubElement(process,
                             self._ns.semantic + self._SEQUENCE_FLOW_SUFFIX,
                             id=self._SEQUENCE_FLOW_PREFIX + to_node + '_out',
                             sourceRef=self._TASK_PREFIX + to_node,
                             targetRef=self._TASK_PREFIX + str(stepcount),
                             nsmap=self._ns.NSMAP)

    def update_grid_heights(self, depthcurr, rounded_height, grid_heights):
        if depthcurr in grid_heights.keys():
            maxheight = grid_heights[depthcurr]
            if rounded_height > maxheight:
                grid_heights[depthcurr] = rounded_height
        else:
            grid_heights[depthcurr] = rounded_height
        return grid_heights

    def _get_chain_heights(self, options, forward_chains):
        grid={}
        gridheights={}
        options_dict = {}
        if self._PROCESS_STEPS_STR == self._PROCESS_STEPS_DIGITAL_STR:
            step_num_id = self._STEP_NUM_ID_DIGITAL
        else:
            step_num_id = self._STEP_NUM_ID
        for opt in options:
            options_dict[opt[step_num_id]]=opt
        column=-1
        parents={}
        parent_columns = {}
        for node in forward_chains.keys():
            subnodes = forward_chains[node]
            if len(subnodes) == 1:
                prev, curr = subnodes[0][0], subnodes[0][1]
                if curr not in parents.keys():
                    parents[curr]=prev
                step = options_dict[curr]
                stepname = step.get(self._PROCESS_STEP_TITLE)
                rows = int(len(stepname) / self._DIVISOR_TASK_ROWS)
                rounded_height = int(self._MULTIPLIER_TASK_TEXT_HEIGHT * rows)
                depthcurr = step.get('depth')
                gridheights= self.update_grid_heights(depthcurr, rounded_height, gridheights)
                if parents[curr] in parent_columns.keys():
                    column = parent_columns[parents[curr]]
                else:
                    column = -1
                if depthcurr in grid.keys():
                    row = grid[depthcurr]
                    if curr not in parent_columns.keys():
                        column+= 1
                        parent_columns[curr]=column
                    row[column] = self._TASK_PREFIX + str(curr)
                    grid[depthcurr] = row
                else:
                    row = {}
                    if curr not in parent_columns.keys():
                        parent_columns[curr]=column+1
                    row[column] = self._TASK_PREFIX + str(curr)
                    grid[depthcurr] = row
                column+=1

                if step.get(self._PROCESS_STEP_EXIT)==self._PROCESS_STEP_EXIT_YES:
                    if depthcurr in grid.keys():
                        row = grid[depthcurr]
                        if curr not in parent_columns.keys():
                            parent_columns[curr] = column
                        row[column] = self._END_EVENT_PREFIX + str(curr)
                        grid[depthcurr] = row
                    else:
                        row = {}
                        if curr not in parent_columns.keys():
                            parent_columns[curr] = column
                        row[column] = self._END_EVENT_PREFIX + str(curr)
                        grid[depthcurr] = row

            else:
                # we have a branch
                suffix=''
                for branch in subnodes:
                    prev, curr = branch[0], branch[1]
                    if curr not in parents.keys():
                        parents[curr] = prev
                    step = options_dict[curr]
                    suffix+=curr+'.'
                    stepname = step.get(self._PROCESS_STEP_TITLE)
                    rows = int(len(stepname) / self._DIVISOR_TASK_ROWS)
                    rounded_height = int(self._MULTIPLIER_TASK_TEXT_HEIGHT * rows)
                    depth = step.get('depth')
                    gridheights = self.update_grid_heights(depth, rounded_height, gridheights)

                for branch in subnodes:
                    prev, curr = branch[0], branch[1]
                    if curr not in parents.keys():
                        parents[curr] = prev
                    else:
                        if parents[curr] in parent_columns.keys():
                            column = parent_columns[parents[curr]]
                        else:
                            column = -1
                    if prev in options_dict.keys():
                        depthprev = options_dict[prev]['depth']
                    else:
                        depthprev=0
                    depthcurr = options_dict[curr]['depth']
                    if depthprev==depthcurr:
                        if depthcurr in grid.keys():
                            row=grid[depthcurr]
                            if curr not in parent_columns.keys():
                                column+=1+1
                                parent_columns[curr] = column
                            row[column-1]=self._EXCLUSIVE_GATEWAY_PREFIX+str(prev)+'_'+suffix[:-1]
                            row[column] =self._TASK_PREFIX + str(curr)
                            grid[depthcurr] = row
                        else:
                            row={}
                            if curr not in parent_columns.keys():
                                column+=1+1
                                parent_columns[curr] = column
                            row[column-1]=self._EXCLUSIVE_GATEWAY_PREFIX+str(prev)+'_'+suffix[:-1]
                            row[column] =self._TASK_PREFIX + str(curr)
                            grid[depthcurr]=row
                    else:
                        if depthcurr in grid.keys():
                            row=grid[depthcurr]
                            if curr not in parent_columns.keys():
                                column += 1+1
                                parent_columns[curr] = column
                            row[column-1]= self._SEQUENCE_FLOW_PREFIX + prev + '.' + curr
                            row[column] = self._TASK_PREFIX + str(curr)
                            grid[depthcurr] = row
                        else:
                            row={}
                            if curr not in parent_columns.keys():
                                column+=1+1
                                parent_columns[curr] = column
                            row[column-1]= self._SEQUENCE_FLOW_PREFIX + prev + '.' + curr
                            row[column] = self._TASK_PREFIX + str(curr)
                            grid[depthcurr]=row
                    if curr not in forward_chains.keys():
                        step=options_dict[curr]
                        if step[self._PROCESS_STEP_EXIT] == self._PROCESS_STEP_EXIT_YES:
                            row=grid[depthcurr]
                            row[column+1]=self._END_EVENT_PREFIX+str(curr)

        reverse_grid={}
        for grid_key in grid.keys():
            row=grid[grid_key]
            for grid_col in row.keys():
                col=row[grid_col]
                reverse_grid[col]=(grid_key, grid_col)

        return options_dict, grid, reverse_grid, gridheights

    def _plot_branch(self, branch, options, chains, chain_heights, stepcount, offset,
                     forward_chains, options_dict, bpmn_plane, xend, ymove):
        curr = branch[1]
        if curr not in forward_chains.keys():
            stepname = options_dict[curr].get(self._PROCESS_STEP_TITLE)
            rows = int(len(stepname) / self._DIVISOR_TASK_ROWS)
            rounded_height = int(self._MULTIPLIER_TASK_TEXT_HEIGHT * rows)
            depth = options_dict[curr].get('depth')
            if depth in self._branches.keys():
                branch = self._branches[depth]
                branch.append([curr, stepname])
                self._branches[depth] = branch
            else:
                branch = []
                branch.append([curr, stepname])
                self._branches[depth] = branch

            bpmn_shape = etree.SubElement(
                bpmn_plane, self._ns.bpmndi + self._SHAPE_SUFFIX,
                id=self._TASK_PREFIX + str(curr) + self._DI_SUFFIX,
                bpmnElement=self._TASK_PREFIX + str(curr),
                nsmap=self._ns.NSMAP)
            etree.SubElement(
                bpmn_shape, self._ns.dc + self._BOUNDS_SUFFIX,
                x=str(xend),
                # y=str(self._Y_SHAPE + ymove),
                y=str(self._Y_SHAPE + ymove + chain_heights[depth]),
                width=str(self._WIDTH_TASK),
                height=str(rounded_height),
                nsmap=self._ns.NSMAP)

        else:
            subnodes = forward_chains[curr]
            stepname = options_dict[curr].get(self._PROCESS_STEP_TITLE)
            rows = int(len(stepname) / self._DIVISOR_TASK_ROWS)
            rounded_height = int(self._MULTIPLIER_TASK_TEXT_HEIGHT * rows)
            depth = options_dict[curr].get('depth')
            if depth in self._branches.keys():
                branch = self._branches[depth]
                branch.append([curr, stepname])
                self._branches[depth] = branch
            else:
                branch = []
                branch.append([curr, stepname])
                self._branches[depth] = branch

            bpmn_shape = etree.SubElement(
                bpmn_plane, self._ns.bpmndi + self._SHAPE_SUFFIX,
                id=self._TASK_PREFIX + str(curr) + self._DI_SUFFIX,
                bpmnElement=self._TASK_PREFIX + str(curr),
                nsmap=self._ns.NSMAP)
            etree.SubElement(
                bpmn_shape, self._ns.dc + self._BOUNDS_SUFFIX,
                x=str(xend),
                y=str(self._Y_SHAPE + ymove + chain_heights[depth]),
                width=str(self._WIDTH_TASK),
                height=str(rounded_height),
                nsmap=self._ns.NSMAP)

            del forward_chains[curr]
            for subn in subnodes:
                self._plot_branch(subn, options, chains, chain_heights, stepcount, offset,
                                  forward_chains, options_dict, bpmn_plane, xend, ymove)

    def _plot_forward_chains(self, options, chains, chain_heights, stepcount, offset,
                             forward_chains, options_dict, bpmn_plane, xend, ymove):
        for node in list(forward_chains):
            if node not in forward_chains.keys():
                continue
            if len(forward_chains[node]) == 1:
                step = options_dict[forward_chains[node][0][1]]
                stepname = step.get(self._PROCESS_STEP_TITLE)
                int(len(stepname) / self._DIVISOR_TASK_ROWS)
                step.get('depth')
            else:
                for branch in forward_chains[node]:
                    self._plot_branch(branch, options, chains, chain_heights, stepcount, offset,
                                      forward_chains, options_dict, bpmn_plane, xend, ymove)

    def _add_branch_node_shapes(self, options, bpmn_plane, stepcount, xcurr, forwardchains):
        options_dict, grid, reverse_grid, grid_heights \
            = self._get_chain_heights(options, forwardchains)
        node_ids=[]
        nodes_left_to_merge=[]
        splits=[]
        ymove = 0
        maxy=0
        left=xcurr
        top=ymove
        parent_xs={}
        xstart = xcurr + self._WIDTH_ARROW + self._WIDTH_RHOMBUS
        rhombuses=0
        end_nodes=0
        rowbaseline = 0
        for key in forwardchains.keys():
            if len(forwardchains[key])>1:
                splits.append(key)
                suffix=''
                depths=[]
                for from_node, to_node in forwardchains[key]:
                    if from_node not in parent_xs.keys():
                        parent_xs[from_node]=(left,top)
                    else:
                        xcurr,ymove = parent_xs[from_node]
                    node_ids.append(int(to_node))
                    suffix=suffix+to_node+'.'
                    depths.append(options_dict[to_node].get('depth'))

                row,col=reverse_grid[self._EXCLUSIVE_GATEWAY_PREFIX + str(key) + '_' + suffix[:-1]]

                bpmn_shape = etree.SubElement(
                    bpmn_plane, self._ns.bpmndi + self._SHAPE_SUFFIX,
                    id=self._EXCLUSIVE_GATEWAY_PREFIX + str(key) + '_' + suffix[:-1]
                       + self._DI_SUFFIX,
                    bpmnElement =self._EXCLUSIVE_GATEWAY_PREFIX + str(key) + '_' + suffix[:-1],
                    isMarkerVisible=self._IS_MARKER_VISIBLE_TRUE, nsmap=self._ns.NSMAP)
                etree.SubElement(
                    bpmn_shape, self._ns.dc + self._BOUNDS_SUFFIX,
                    x=str(xcurr + self._WIDTH_ARROW),
                    y=str(self._Y_SHAPE + ymove),
                    width=str(self._WIDTH_RHOMBUS),
                    height=str(self._HEIGHT_RHOMBUS),
                    nsmap=self._ns.NSMAP)
                bpmn_label = etree.SubElement(
                    bpmn_shape, self._ns.bpmndi + self._LABEL_SUFFIX,
                    nsmap=self._ns.NSMAP)
                etree.SubElement(bpmn_label, self._ns.dc + self._BOUNDS_SUFFIX,
                                 x=str(xcurr + self._WIDTH_ARROW),
                                 # x=str(xcurr + self._OFFSET_BOUNDS +col*columnWidth),
                                 y=str(self._Y_LABEL_VARIANT+ymove),
                                 width=str(self._WIDTH_LABEL_VARIANT),
                                 height=str(self._HEIGHT_LABEL_VARIANT),
                                 nsmap=self._ns.NSMAP)
                head = self._TASK_PREFIX
                maxy=max(self._Y_SHAPE + row*self._rowHeight,
                         self._Y_LABEL_VARIANT+row*self._rowHeight,maxy)
                if stepcount == 2:
                    head = self._START_EVENT_PREFIX
                # Draw an edge from the previous node to the ExclusiveGateway node
                bpmn_edge = etree.SubElement(
                    bpmn_plane, self._ns.bpmndi + self._EDGE_SUFFIX,
                    id=self._SEQUENCE_FLOW_PREFIX + str(key) + self._DI_SUFFIX,
                    bpmnElement=self._SEQUENCE_FLOW_PREFIX + str(key),
                    sourceElement=head + str(key),
                    targetElement=self._EXCLUSIVE_GATEWAY_PREFIX + str(key) + '_' + suffix[:-1],
                    nsmap=self._ns.NSMAP)
                self._create_waypoint(bpmn_edge, xcurr, self._Y_START + ymove)
                self._create_waypoint(bpmn_edge, xcurr + self._WIDTH_ARROW, self._Y_START + ymove)
                bpmn_label = etree.SubElement(
                    bpmn_edge, self._ns.bpmndi + self._LABEL_SUFFIX,
                    nsmap=self._ns.NSMAP)
                etree.SubElement(
                    bpmn_label, self._ns.dc + self._BOUNDS_SUFFIX,
                    x=str(round((xcurr + self._WIDTH_ARROW) / 2+col*self._columnWidth)),
                    y=str(self._Y_LABEL+row*self._rowHeight),
                    width=str(self._WIDTH_LABEL),
                    height=str(self._HEIGHT_LABEL),
                    nsmap=self._ns.NSMAP)
                maxy=max(self._Y_LABEL+row*self._rowHeight,maxy)
                for from_node, to_node in forwardchains[key]:
                    node_ids.append(int(to_node))
                    step = options_dict[to_node]
                    if to_node not in forwardchains.keys():
                        if step[self._PROCESS_STEP_EXIT] != self._PROCESS_STEP_EXIT_YES:
                            nodes_left_to_merge.append(options_dict[to_node])
                        # else:
                        #     print('Skipping ',to_node)

                    row, col = reverse_grid[self._TASK_PREFIX + to_node]
                    stepname = step.get(self._PROCESS_STEP_TITLE)
                    rows = int(len(stepname) / self._DIVISOR_TASK_ROWS)
                    rounded_height = int(self._MULTIPLIER_TASK_TEXT_HEIGHT * rows)

                    bpmn_shape = etree.SubElement(
                        bpmn_plane, self._ns.bpmndi + self._SHAPE_SUFFIX,
                        id=self._TASK_PREFIX + to_node + self._DI_SUFFIX,
                        bpmnElement=self._TASK_PREFIX + to_node,
                        nsmap=self._ns.NSMAP)
                    xnew = xstart + (self._WIDTH_ARROW + self._WIDTH_TASK) * (col-1) \
                           - rhombuses*self._WIDTH_RHOMBUS
                    xcurr = xnew + (self._WIDTH_ARROW + self._WIDTH_TASK)
                    curr_height=0
                    for i in range(row):
                        curr_height+= grid_heights[i]+self._HEIGHT_LABEL
                    ymove = max(row*self._rowHeight, curr_height)
                    if to_node not in parent_xs.keys():
                        parent_xs[to_node]=(xcurr,ymove)
                    else:
                        xcurr,ymove = parent_xs[to_node]

                    etree.SubElement(
                        bpmn_shape, self._ns.dc + self._BOUNDS_SUFFIX,
                        x=str(xnew + self._WIDTH_ARROW),
                        y=str(self._Y_SHAPE + ymove),
                        width=str(self._WIDTH_TASK),
                        height=str(rounded_height),
                        nsmap=self._ns.NSMAP)
                    maxy = max(self._Y_SHAPE + ymove, maxy)

                    # Add timer icon in branched nodes
                    bpmn_shape = etree.SubElement(
                        bpmn_plane, self._ns.bpmndi + self._SHAPE_SUFFIX,
                        id=self._TASK_PREFIX + to_node + '_Timer_' + to_node,
                        bpmnElement=self._TIMER_PREFIX + to_node,
                        nsmap=self._ns.NSMAP)
                    etree.SubElement(
                        bpmn_shape, self._ns.dc + self._BOUNDS_SUFFIX,
                        x=str(xcurr - 15),
                        y=str(ymove + self._Y_LABEL_VARIANT + rounded_height + 10),
                        width=str(32),
                        height=str(32),
                        nsmap=self._ns.NSMAP)
                    bpmn_label = etree.SubElement(
                        bpmn_shape, self._ns.bpmndi + self._LABEL_SUFFIX,
                        nsmap=self._ns.NSMAP)
                    etree.SubElement(bpmn_label,
                                     self._ns.dc + self._BOUNDS_SUFFIX,
                                     x=str(xcurr - self._TASK_WIDTH + 30),
                                     y=str(ymove + self._Y_LABEL_VARIANT + rounded_height + 32),
                                     width=str(self._WIDTH_LABEL_VARIANT),
                                     height=str(self._HEIGHT_LABEL_VARIANT),
                                     nsmap=self._ns.NSMAP)
                    maxy = max(ymove + self._Y_LABEL_VARIANT + rounded_height + 10,
                               ymove + self._Y_LABEL_VARIANT + rounded_height + 32, maxy)

                    branch=False
                    if self._SEQUENCE_FLOW_PREFIX + from_node + '.' \
                            + to_node in reverse_grid.keys():
                        row, col = reverse_grid[self._SEQUENCE_FLOW_PREFIX
                                                + from_node + '.' + to_node]
                        xnew = xstart + (self._WIDTH_ARROW + self._WIDTH_TASK) * col \
                               - rhombuses*self._WIDTH_RHOMBUS
                        xcurr = xnew + (self._WIDTH_ARROW + self._WIDTH_TASK)
                        curr_height = 0
                        for i in range(row):
                            curr_height += grid_heights[i] + self._HEIGHT_LABEL
                        ymove = max(row * self._rowHeight, curr_height)
                        branch=True

                    bpmn_edge = etree.SubElement(
                        bpmn_plane, self._ns.bpmndi + self._EDGE_SUFFIX,
                        id=self._SEQUENCE_FLOW_PREFIX + from_node + '.' + to_node + self._DI_SUFFIX,
                        bpmnElement=self._SEQUENCE_FLOW_PREFIX + from_node + '.' + to_node,
                        sourceElement=self._EXCLUSIVE_GATEWAY_PREFIX + from_node+'_'+suffix[:-1],
                        targetElement=self._TASK_PREFIX + to_node,
                        nsmap=self._ns.NSMAP)

                    if rowbaseline==0:
                        rowbaseline=self._Y_START + ymove
                    if branch:
                        self._create_waypoint(bpmn_edge, xnew, rowbaseline)
                        rowbaseline = self._Y_START + ymove
                    self._create_waypoint(bpmn_edge, xnew, rowbaseline)
                    self._create_waypoint(bpmn_edge, xnew + self._WIDTH_ARROW, rowbaseline)
                    bpmn_label = etree.SubElement(
                        bpmn_edge, self._ns.bpmndi + self._LABEL_SUFFIX,
                        nsmap=self._ns.NSMAP)
                    etree.SubElement(
                        bpmn_label, self._ns.dc + self._BOUNDS_SUFFIX,
                        x=str(round(xnew + self._WIDTH_ARROW / 2)),
                        y=str(self._Y_LABEL),
                        width=str(self._WIDTH_LABEL),
                        height=str(self._HEIGHT_LABEL),
                        nsmap=self._ns.NSMAP)

                    if step[self._PROCESS_STEP_EXIT] == self._PROCESS_STEP_EXIT_YES:
                        rhombuses = self._add_end_node_shapes(rhombuses, end_nodes, to_node,
                                                              bpmn_plane, maxy, parent_xs)
                rhombuses+=1

#################################################
            elif len(forwardchains[key])==1:
                from_node, to_node = forwardchains[key][0]
                node_ids.append(int(to_node))

                step = options_dict[to_node]
                if to_node not in forwardchains.keys():
                    if step[self._PROCESS_STEP_EXIT] != self._PROCESS_STEP_EXIT_YES:
                        nodes_left_to_merge.append(options_dict[to_node])
                    # else:
                    #     print('Skipping ', to_node)

                row, col = reverse_grid[self._TASK_PREFIX + to_node]

                step = options_dict[to_node]
                stepname = step.get(self._PROCESS_STEP_TITLE)
                rows = int(len(stepname) / self._DIVISOR_TASK_ROWS)
                rounded_height = int(self._MULTIPLIER_TASK_TEXT_HEIGHT * rows)
                bpmn_shape = etree.SubElement(
                    bpmn_plane, self._ns.bpmndi + self._SHAPE_SUFFIX,
                    id=self._TASK_PREFIX + to_node + self._DI_SUFFIX,
                    bpmnElement=self._TASK_PREFIX + to_node,
                    nsmap=self._ns.NSMAP)

                xnew = xstart + (self._WIDTH_ARROW + self._WIDTH_TASK) * (col-1)  \
                       - rhombuses * self._WIDTH_RHOMBUS + self._WIDTH_ARROW
                xcurr = xnew + (self._WIDTH_ARROW + self._WIDTH_TASK)
                curr_height = 0
                for i in range(row):
                    curr_height += grid_heights[i] + self._HEIGHT_LABEL
                ymove = max(row * self._rowHeight, curr_height)
                if to_node not in parent_xs.keys():
                    parent_xs[to_node] = (xcurr, ymove)
                else:
                    xcurr, ymove = parent_xs[to_node]
                etree.SubElement(
                    bpmn_shape, self._ns.dc + self._BOUNDS_SUFFIX,
                    x=str(xnew + self._WIDTH_ARROW),
                    y=str(self._Y_SHAPE + ymove),width=str(self._WIDTH_TASK),
                        height=str(rounded_height),nsmap=self._ns.NSMAP)

                # Add timer icon in branched nodes
                bpmn_shape = etree.SubElement(
                    bpmn_plane, self._ns.bpmndi + self._SHAPE_SUFFIX,
                    id=self._TASK_PREFIX + to_node + '_Timer_' + to_node,
                    bpmnElement=self._TIMER_PREFIX + to_node,
                    nsmap=self._ns.NSMAP)
                etree.SubElement(
                    bpmn_shape, self._ns.dc + self._BOUNDS_SUFFIX,
                    x=str(xcurr - 15),
                    y=str(ymove + self._Y_LABEL_VARIANT + rounded_height + 10),
                    width=str(32),
                    height=str(32),
                    nsmap=self._ns.NSMAP)
                bpmn_label = etree.SubElement(
                    bpmn_shape, self._ns.bpmndi + self._LABEL_SUFFIX,
                    nsmap=self._ns.NSMAP)
                etree.SubElement(bpmn_label,
                                 self._ns.dc + self._BOUNDS_SUFFIX,
                                 x=str(xcurr - self._TASK_WIDTH + 30),
                                 y=str(ymove + self._Y_LABEL_VARIANT + rounded_height + 32),
                                 width=str(self._WIDTH_LABEL_VARIANT),
                                 height=str(self._HEIGHT_LABEL_VARIANT),
                                 nsmap=self._ns.NSMAP)
                maxy = max(ymove + self._Y_LABEL_VARIANT + rounded_height + 10,
                           ymove + self._Y_LABEL_VARIANT + rounded_height + 32, maxy)

                bpmn_edge = etree.SubElement(
                    bpmn_plane, self._ns.bpmndi + self._EDGE_SUFFIX,
                    id=self._SEQUENCE_FLOW_PREFIX + from_node + '.' + to_node + self._DI_SUFFIX,
                    bpmnElement=self._SEQUENCE_FLOW_PREFIX + from_node + '.' + to_node,
                    sourceElement=self._TASK_PREFIX + from_node,
                    targetElement=self._TASK_PREFIX + to_node,
                    nsmap=self._ns.NSMAP)
                self._create_waypoint(bpmn_edge, xnew, self._Y_START + ymove)
                self._create_waypoint(bpmn_edge, xnew + self._WIDTH_ARROW, self._Y_START + ymove)
                bpmn_label = etree.SubElement(
                    bpmn_edge, self._ns.bpmndi + self._LABEL_SUFFIX,
                    nsmap=self._ns.NSMAP)
                etree.SubElement(
                    bpmn_label, self._ns.dc + self._BOUNDS_SUFFIX,
                    x=str(round(xnew + self._WIDTH_ARROW / 2)),
                    y=str(self._Y_LABEL),
                    width=str(self._WIDTH_LABEL),
                    height=str(self._HEIGHT_LABEL),
                    nsmap=self._ns.NSMAP)

                if step[self._PROCESS_STEP_EXIT] == self._PROCESS_STEP_EXIT_YES:
                    rhombuses= self._add_end_node_shapes(rhombuses, end_nodes, to_node, bpmn_plane,
                                                         maxy, parent_xs)
        return maxy, nodes_left_to_merge, max(node_ids), rhombuses, grid, reverse_grid, grid_heights

    def _add_end_node_shapes(self, rhombuses, end_nodes, to_node, bpmn_plane, maxy, parent_xs):
        xcurr, ymove = parent_xs[to_node]

        bpmn_shape = etree.SubElement(
            bpmn_plane, self._ns.bpmndi + self._SHAPE_SUFFIX,
            id=self._END_EVENT_PREFIX + to_node + '_end' + self._DI_SUFFIX,
            bpmnElement=self._END_EVENT_PREFIX + to_node + '_end',
            nsmap=self._ns.NSMAP)
        etree.SubElement(
            bpmn_shape, self._ns.dc + self._BOUNDS_SUFFIX,
            x=str(xcurr + self._WIDTH_ARROW),
            y=str(self._Y_SHAPE_VARIANT + ymove),
            width=str(self._WIDTH_START_EVENT),
            height=str(self._WIDTH_START_EVENT), nsmap=self._ns.NSMAP)
        bpmn_label = etree.SubElement(
            bpmn_shape, self._ns.bpmndi + self._LABEL_SUFFIX,
            nsmap=self._ns.NSMAP)
        etree.SubElement(
            bpmn_label, self._ns.dc + self._BOUNDS_SUFFIX,
            x=str(round(xcurr + self._WIDTH_ARROW / 2)),
            y=str(self._Y_SHAPE_VARIANT_2 + ymove),
            width=str(self._WIDTH_LABEL),
            height=str(self._HEIGHT_LABEL),
            nsmap=self._ns.NSMAP)
        maxy = max(self._Y_SHAPE_VARIANT + ymove, self._Y_SHAPE_VARIANT_2 + ymove, maxy)

        bpmn_edge = etree.SubElement(
            bpmn_plane, self._ns.bpmndi + self._EDGE_SUFFIX,
            id=self._SEQUENCE_FLOW_PREFIX + to_node + '_out' + self._DI_SUFFIX,
            bpmnElement=self._SEQUENCE_FLOW_PREFIX + to_node + '_out',
            sourceElement=self._TASK_PREFIX + to_node,
            targetElement=self._END_EVENT_PREFIX + to_node + '_end',
            nsmap=self._ns.NSMAP)
        self._create_waypoint(bpmn_edge, xcurr, self._Y_START + ymove)
        self._create_waypoint(bpmn_edge, xcurr + self._WIDTH_ARROW, self._Y_START + ymove)
        bpmn_label = etree.SubElement(
            bpmn_edge, self._ns.bpmndi + self._LABEL_SUFFIX,
            nsmap=self._ns.NSMAP)
        etree.SubElement(
            bpmn_label, self._ns.dc + self._BOUNDS_SUFFIX,
            x=str(round(xcurr + self._WIDTH_ARROW / 2)),
            y=str(self._Y_LABEL + ymove),
            width=str(self._WIDTH_LABEL),
            height=str(self._HEIGHT_LABEL),
            nsmap=self._ns.NSMAP)
        end_nodes += 1
        maxy = max(self._Y_LABEL + ymove, maxy)
        return rhombuses

    def _add_merge_node_shapes(self, bpmn_plane, stepcount, xcurr, rounded_height,
                            nodes_left_to_merge, max_node_id, grid, grid_heights):
        head = self._TASK_PREFIX
        next_node_ids=-1
        xend=-1
        offsets=self._get_grid_width(grid)
        start = xcurr
        offsets=[sum(row) for row in offsets]
        if len(nodes_left_to_merge)>0:
            for node in nodes_left_to_merge:
                depth=node.get('depth')
                nodeid=node.get(self._PROCESS_STEP_NUM_ID)
                next_node_ids=str(max_node_id + 1)
                currstart = start + offsets[depth]
                xend = start + max(offsets) + 2*self._WIDTH_ARROW
                xmid = xend-self._ARROW_WIDTH

                bpmn_edge = etree.SubElement(
                    bpmn_plane, self._ns.bpmndi + self._EDGE_SUFFIX,
                    id=self._SEQUENCE_FLOW_PREFIX + nodeid + '_out_di',
                    bpmnElement=self._SEQUENCE_FLOW_PREFIX + nodeid + '_out',
                    sourceElement=self._TASK_PREFIX + nodeid,
                    targetElement=head + next_node_ids,
                    nsmap=self._ns.NSMAP)
                bpmn_label = etree.SubElement(bpmn_edge,
                                             self._ns.bpmndi + self._LABEL_SUFFIX,
                                             nsmap=self._ns.NSMAP)
                if depth == 0:
                    self._create_waypoint(bpmn_edge, currstart, self._Y_START)
                    self._create_waypoint(bpmn_edge, xend, self._Y_START)
                    etree.SubElement(
                        bpmn_label, self._ns.dc + self._BOUNDS_SUFFIX,
                        x=str(xmid),
                        y=str(self._Y_LABEL),
                        width=str(self._WIDTH_LABEL),
                        height=str(self._HEIGHT_LABEL),
                        nsmap=self._ns.NSMAP)
                else:
                    curr_height = 0
                    for i in range(depth):
                        curr_height += grid_heights[i] + self._HEIGHT_LABEL
                    ymove = max(depth * self._rowHeight, curr_height)
                    self._create_waypoint(bpmn_edge, currstart, self._Y_START + ymove)
                    self._create_waypoint(bpmn_edge, xmid, self._Y_START + ymove)
                    self._create_waypoint(bpmn_edge, xmid, self._Y_START)
                    self._create_waypoint(bpmn_edge, xend, self._Y_START)
                    etree.SubElement(
                        bpmn_label, self._ns.dc + self._BOUNDS_SUFFIX,
                        x=str(xmid),
                        y=str(self._Y_START + self._rowHeight * depth - self._OFFSET_Y_LABEL),
                        width=str(self._WIDTH_LABEL),
                        height=str(self._HEIGHT_LABEL),
                        nsmap=self._ns.NSMAP)
        elif len(nodes_left_to_merge)==0 and int(next_node_ids)<0:
            return 0,False

        if int(next_node_ids)>0:
            bpmn_shape = etree.SubElement(
                bpmn_plane, self._ns.bpmndi + self._SHAPE_SUFFIX,
                id=head + str(next_node_ids) + self._DI_SUFFIX,
                bpmnElement=head + str(next_node_ids),
                nsmap=self._ns.NSMAP)
            etree.SubElement(
                bpmn_shape, self._ns.dc + self._BOUNDS_SUFFIX,
                x=str(xend),
                y=str(self._Y_START - self._OFFSET_BOUNDS),
                width=str(self._WIDTH_TASK),
                height=str(rounded_height),
                nsmap=self._ns.NSMAP)

            # Add timer icon main flow after branch
            bpmn_shape = etree.SubElement(
                bpmn_plane, self._ns.bpmndi + self._SHAPE_SUFFIX,
                id=f'{self._TASK_PREFIX}{stepcount}_Timer_{stepcount}',
                bpmnElement=self._TIMER_PREFIX + str(stepcount),
                nsmap=self._ns.NSMAP)
            etree.SubElement(
                bpmn_shape, self._ns.dc + self._BOUNDS_SUFFIX,
                x=str(xend +self._WIDTH_TASK- 15),
                y=str(self._Y_LABEL_VARIANT + rounded_height + 10),
                width=str(32),
                height=str(32),
                nsmap=self._ns.NSMAP)
            bpmn_label = etree.SubElement(
                bpmn_shape, self._ns.bpmndi + self._LABEL_SUFFIX,
                nsmap=self._ns.NSMAP)
            y_pos = str(self._Y_LABEL_VARIANT + rounded_height + 32)
            etree.SubElement(bpmn_label, self._ns.dc + self._BOUNDS_SUFFIX,
                             x=str(xend + 30),
                             y=y_pos,
                             width=str(self._WIDTH_LABEL_VARIANT),
                             height=str(self._HEIGHT_LABEL_VARIANT),
                             nsmap=self._ns.NSMAP)
        return xend+self._WIDTH_TASK, True

    def _handle_plain_node_shapes(self, options, bpmn_plane, stepcount, plane_height, xcurr,
                               rounded_height):
        if len(options) == 0:
            bpmn_shape = etree.SubElement(
                bpmn_plane, self._ns.bpmndi + self._SHAPE_SUFFIX,
                id=self._TASK_PREFIX + str(stepcount) + self._DI_SUFFIX,
                bpmnElement=self._TASK_PREFIX + str(stepcount),
                nsmap=self._ns.NSMAP)
            etree.SubElement(
                bpmn_shape, self._ns.dc + self._BOUNDS_SUFFIX,
                x=str(xcurr + self._WIDTH_ARROW),
                y=str(self._Y_SHAPE_VARIANT),
                width=str(self._WIDTH_TASK),
                height=str(rounded_height),
                nsmap=self._ns.NSMAP)
            new_plane_height = rounded_height
            plane_height = max(plane_height, new_plane_height)
            head = self._TASK_PREFIX
            bpmn_edge = etree.SubElement(
                bpmn_plane, self._ns.bpmndi + self._EDGE_SUFFIX,
                id=self._SEQUENCE_FLOW_PREFIX + str(
                    stepcount - 1) + self._DI_SUFFIX,
                bpmnElement=self._SEQUENCE_FLOW_PREFIX + str(stepcount - 1),
                sourceElement=head + str(stepcount - 1),
                targetElement=self._TASK_PREFIX + str(stepcount),
                nsmap=self._ns.NSMAP)
            self._create_waypoint(bpmn_edge, xcurr, self._Y_START)
            self._create_waypoint(bpmn_edge, xcurr + self._WIDTH_ARROW, self._Y_START)
            bpmn_label = etree.SubElement(
                bpmn_edge, self._ns.bpmndi + self._LABEL_SUFFIX,
                nsmap=self._ns.NSMAP)
            etree.SubElement(
                bpmn_label, self._ns.dc + self._BOUNDS_SUFFIX,
                x=str(round((xcurr + self._WIDTH_ARROW) / 2)),
                y=str(self._Y_LABEL),
                width=str(self._WIDTH_LABEL),
                height=str(self._HEIGHT_LABEL),
                nsmap=self._ns.NSMAP)
            max_chain_length = 0
            xcurr += self._WIDTH_ARROW + self._WIDTH_TASK

            # add timer icon main flow
            bpmn_shape = etree.SubElement(
                bpmn_plane, self._ns.bpmndi + self._SHAPE_SUFFIX,
                id=f'{self._TASK_PREFIX}{stepcount}_Timer_{stepcount}',
                bpmnElement=self._TIMER_PREFIX + str(stepcount),
                nsmap=self._ns.NSMAP)
            etree.SubElement(
                bpmn_shape, self._ns.dc + self._BOUNDS_SUFFIX,
                x=str(xcurr - 15),
                y=str(self._Y_LABEL_VARIANT + rounded_height + 10),
                width=str(32),
                height=str(32),
                nsmap=self._ns.NSMAP)
            bpmn_label = etree.SubElement(
                bpmn_shape, self._ns.bpmndi + self._LABEL_SUFFIX,
                nsmap=self._ns.NSMAP)
            y_pos = str(self._Y_LABEL_VARIANT + rounded_height + 32)
            etree.SubElement(bpmn_label, self._ns.dc + self._BOUNDS_SUFFIX,
                             x=str(xcurr - self._TASK_WIDTH + 30),
                             y=y_pos,
                             width=str(self._WIDTH_LABEL_VARIANT),
                             height=str(self._HEIGHT_LABEL_VARIANT),
                             nsmap=self._ns.NSMAP)

            has_end_node=True
        else:
            _, max_chain_length, forward_chains, _ = self.group_options(options)
            branch_height, nodes_left_to_merge, max_node_id, _, grid, _, grid_heights \
                = self._add_branch_node_shapes(options, bpmn_plane, stepcount, xcurr,
                                               forward_chains)
            xcurr, has_end_node = self._add_merge_node_shapes(bpmn_plane, stepcount, xcurr,
                                                              rounded_height, nodes_left_to_merge,
                                                              max_node_id, grid, grid_heights)
            plane_height = max(plane_height, branch_height)
        return plane_height, max_chain_length, xcurr, has_end_node

    def _append_shapes_and_edges(self, bpmn_plane):
        branch_height = 0
        stepcount = 0
        plane_height = 0
        totalchainlength = 0
        options = []
        allnodes = []
        has_end_node=False
        xcurr = self._OFFSET_X_APPEND_SHAPES_AND_EDGES
        bpmn_shape = etree.SubElement(
            bpmn_plane, self._ns.bpmndi + self._SHAPE_SUFFIX,
            id=self._START_EVENT_0 + self._DI_SUFFIX,
            bpmnElement=self._START_EVENT_0, nsmap=self._ns.NSMAP)
        etree.SubElement(
            bpmn_shape, self._ns.dc + self._BOUNDS_SUFFIX,
            x=str(xcurr),
            y=str(self._Y_SHAPE_VARIANT),
            width=str(self._WIDTH_START_EVENT),
            height=str(self._WIDTH_START_EVENT),
            nsmap=self._ns.NSMAP)
        bpmn_label = etree.SubElement(
            bpmn_shape, self._ns.bpmndi + self._LABEL_SUFFIX,
            nsmap=self._ns.NSMAP)
        etree.SubElement(
            bpmn_label, self._ns.dc + self._BOUNDS_SUFFIX,
            x=str(xcurr - self._OFFSET_X_LABEL),
            y=str(self._Y_SHAPE_VARIANT_2),
            width=str(self._WIDTH_LABEL),
            height=str(self._HEIGHT_LABEL),
            nsmap=self._ns.NSMAP)
        bpmn_edge = etree.SubElement(
            bpmn_plane, self._ns.bpmndi + self._EDGE_SUFFIX,
            id=self._SEQUENCE_FLOW_0 + self._DI_SUFFIX,
            bpmnElement=self._SEQUENCE_FLOW_0,
            sourceElement=self._START_EVENT_0,
            targetElement=self._TASK_1_NAME,
            nsmap=self._ns.NSMAP)
        self._create_waypoint(bpmn_edge, xcurr + self._WIDTH_START_EVENT, self._Y_START)
        self._create_waypoint(bpmn_edge, xcurr + self._WIDTH_START_EVENT + self._WIDTH_ARROW,
                              self._Y_START)
        bpmn_label = etree.SubElement(
            bpmn_edge, self._ns.bpmndi + self._LABEL_SUFFIX,
            nsmap=self._ns.NSMAP)
        etree.SubElement(
            bpmn_label, self._ns.dc + self._BOUNDS_SUFFIX,
            x=str(stepcount * self._WIDTH_TASK),
            y=str(self._Y_LABEL),
            width=str(self._WIDTH_LABEL),
            height=str(self._HEIGHT_LABEL),
            nsmap=self._ns.NSMAP)
        xcurr += self._WIDTH_START_EVENT + self._WIDTH_ARROW
        rounded_heights = []
        timers = []
        children_dict = {}
        for _, step in self._process_steps.items():
            if step.get(self._PROCESS_STEP_CHILD) == self._PROCESS_STEP_CHILD_YES:
                step.get(self._PROCESS_STEP_NUM_ID)
                parent_id = int(step.get(self._PROCESS_STEP_PREVIOUS_CHILD))
                if parent_id in children_dict:
                    children_dict[parent_id] = children_dict[parent_id] + 1
                else:
                    children_dict[parent_id] = 0
                sibling_count = children_dict[parent_id]
                parent_depth = int(self._process_steps.get(parent_id).get('depth'))
                if parent_depth == 0:
                    step['depth'] = sibling_count
                else:
                    step['depth'] = sibling_count + parent_depth
            else:
                step['depth'] = 0

        for _, step in self._process_steps.items():
            stepcount += 1
            if step.get(self._PROCESS_STEP_TITLE) is not None:
                if self._PROCESS_STEPS_STR == self._PROCESS_STEPS_DIGITAL_STR:
                    timer = (step.get(self._PROCESS_STEP_DIGITAL_DURATION_MIN),
                             step.get(self._PROCESS_STEP_DIGITAL_DURATION_MAX),
                             step.get(self._PROCESS_STEP_DIGITAL_DURATION_TYPE))
                else:
                    timer = (step.get(self._PROCESS_STEP_DURATION_MIN),
                             step.get(self._PROCESS_STEP_DURATION_MAX),
                             step.get(self._PROCESS_STEP_DURATION_TYPE))

                timers.append(timer)
                stepname = step.get(self._PROCESS_STEP_TITLE)
                rows = int(len(stepname) / self._DIVISOR_TASK_ROWS)
                rounded_height = int(self._MULTIPLIER_TASK_TEXT_HEIGHT * rows)
                rounded_heights.append(rounded_height)
                if stepcount == 1:
                    bpmn_shape = etree.SubElement(
                        bpmn_plane, self._ns.bpmndi + self._SHAPE_SUFFIX,
                        id=self._TASK_PREFIX + str(
                            stepcount) + self._DI_SUFFIX,
                        bpmnElement=self._TASK_PREFIX + str(stepcount),
                        nsmap=self._ns.NSMAP)
                    etree.SubElement(
                        bpmn_shape, self._ns.dc + self._BOUNDS_SUFFIX,
                        x=str(xcurr),
                        y=str(self._Y_SHAPE_VARIANT),
                        width=str(self._WIDTH_TASK),
                        height=str(rounded_height),
                        nsmap=self._ns.NSMAP)
                    allnodes.append(self._TASK_PREFIX + str(stepcount))
                    xcurr += self._WIDTH_TASK

                    # add timer icon
                    id_ = f'{self._TASK_PREFIX}{stepcount}_Timer_{stepcount}'
                    bpmn_shape = etree.SubElement(
                        bpmn_plane, self._ns.bpmndi + self._SHAPE_SUFFIX,
                        id=id_,
                        bpmnElement=self._TIMER_PREFIX + str(stepcount),
                        nsmap=self._ns.NSMAP)
                    etree.SubElement(
                        bpmn_shape, self._ns.dc + self._BOUNDS_SUFFIX,
                        x=str(xcurr - 15),
                        y=str(self._Y_LABEL_VARIANT + rounded_height + 10),
                        width=str(32),
                        height=str(32),
                        nsmap=self._ns.NSMAP)
                    bpmn_label = etree.SubElement(
                        bpmn_shape, self._ns.bpmndi + self._LABEL_SUFFIX,
                        nsmap=self._ns.NSMAP)
                    y_doc = str(
                        self._Y_LABEL_VARIANT + rounded_height + 32)
                    etree.SubElement(bpmn_label,
                                     self._ns.dc + self._BOUNDS_SUFFIX,
                                     x=str(xcurr - self._TASK_WIDTH + 30),
                                     y=y_doc,
                                     width=str(self._WIDTH_LABEL_VARIANT),
                                     height=str(self._HEIGHT_LABEL_VARIANT),
                                     nsmap=self._ns.NSMAP)

                else:
                    if step.get(self._PROCESS_STEP_CHILD) == \
                            self._PROCESS_STEP_CHILD_YES:
                        options.append(step)
                    else:
                        plane_height, max_branch_length, xcurr, has_end_node = \
                            self._handle_plain_node_shapes(options, bpmn_plane, stepcount,
                                                           plane_height, xcurr, rounded_height)
                        options = []
                        totalchainlength += max_branch_length
                        allnodes.append(self._TASK_PREFIX + str(stepcount))
        if has_end_node and len(options)==0:
            bpmn_shape = etree.SubElement(
                bpmn_plane, self._ns.bpmndi + self._SHAPE_SUFFIX,
                id=self._END_EVENT_PREFIX + str(stepcount + 1) + self._DI_SUFFIX,
                bpmnElement=self._END_EVENT_PREFIX + str(stepcount + 1),
                nsmap=self._ns.NSMAP)
            etree.SubElement(
                bpmn_shape, self._ns.dc + self._BOUNDS_SUFFIX,
                x=str(xcurr + self._WIDTH_ARROW),
                y=str(self._Y_SHAPE_VARIANT), width=str(self._WIDTH_START_EVENT),
                height=str(self._WIDTH_START_EVENT), nsmap=self._ns.NSMAP)
            bpmn_label = etree.SubElement(
                bpmn_shape, self._ns.bpmndi + self._LABEL_SUFFIX,
                nsmap=self._ns.NSMAP)
            etree.SubElement(
                bpmn_label, self._ns.dc + self._BOUNDS_SUFFIX,
                x=str(round(xcurr + self._WIDTH_ARROW / 2)),
                y=str(self._Y_SHAPE_VARIANT_2),
                width=str(self._WIDTH_LABEL),
                height=str(self._HEIGHT_LABEL),
                nsmap=self._ns.NSMAP)
            bpmn_edge = etree.SubElement(
                bpmn_plane, self._ns.bpmndi + self._EDGE_SUFFIX,
                id=self._SEQUENCE_FLOW_PREFIX + str(stepcount) + self._DI_SUFFIX,
                bpmnElement=self._SEQUENCE_FLOW_PREFIX + str(stepcount),
                sourceElement=self._TASK_PREFIX + str(stepcount),
                targetElement=self._END_EVENT_PREFIX + str(stepcount + 1),
                nsmap=self._ns.NSMAP)
            self._create_waypoint(bpmn_edge, xcurr, self._Y_START)
            self._create_waypoint(bpmn_edge, xcurr + self._WIDTH_ARROW, self._Y_START)
            bpmn_label = etree.SubElement(
                bpmn_edge, self._ns.bpmndi + self._LABEL_SUFFIX,
                nsmap=self._ns.NSMAP)
            etree.SubElement(
                bpmn_label, self._ns.dc + self._BOUNDS_SUFFIX,
                x=str(round(xcurr + self._WIDTH_ARROW / 2)),
                y=str(self._Y_LABEL),
                width=str(self._WIDTH_LABEL),
                height=str(self._HEIGHT_LABEL),
                nsmap=self._ns.NSMAP)
            xcurr += self._WIDTH_LABEL
        elif len(options) > 0:
            _, _, forward_chains, _ = self.group_options(options)
            branch_height, _, _, _, grid, _, _ = self._add_branch_node_shapes(options, bpmn_plane,
                                                                             stepcount, xcurr,
                                                                             forward_chains)
            offsets_plain = self._get_grid_width(grid)
            offsets_flat = [sum(row) for row in offsets_plain]
            xcurr +=max(offsets_flat)
        # else:
        #     print('Check This Too!!')

        plane_height=max(plane_height, branch_height, max(rounded_heights))


        return plane_height + self._OFFSET_X_APPEND_SHAPES_AND_EDGES, xcurr

    def _get_grid_width(self, grid):
        offsets=[]
        for k in grid.keys():
            row = grid[k]
            minkey=min(row.keys())
            if minkey==0:
                offset=[]
                for col_keys in row.keys():
                    col = row[col_keys]
                    if col.startswith('ExclusiveGateway'):
                        offset.append(self._WIDTH_RHOMBUS+self._WIDTH_ARROW)
                    elif col.startswith('Task'):
                        offset.append(self._WIDTH_TASK + self._WIDTH_ARROW)
                    elif col.startswith('SequenceFlow'):
                        offset.append(self._WIDTH_RHOMBUS + self._WIDTH_ARROW)
                    elif col.startswith('EndEvent'):
                        offset.append(self._WIDTH_RHOMBUS)
                offsets.append(offset)
            else:
                offsets_lists=[offsets[i][:minkey] for i in range(k)]
                max_offset=max(sum(l) for l in offsets_lists)
                offset=[max_offset]
                for col_keys in row.keys():
                    col = row[col_keys]
                    if col.startswith('ExclusiveGateway'):
                        offset.append(self._WIDTH_RHOMBUS+self._WIDTH_ARROW)
                    elif col.startswith('Task'):
                        offset.append(self._WIDTH_TASK + self._WIDTH_ARROW)
                    elif col.startswith('SequenceFlow'):
                        offset.append(self._WIDTH_RHOMBUS + self._WIDTH_ARROW)
                    elif col.startswith('EndEvent'):
                        offset.append(self._WIDTH_RHOMBUS)
                offsets.append(offset)
        return offsets

    def _append_data_object_shapes(self, bpmn_plane, plane_height, bounds_width):
        # Now add the shapes for the Evidences
        stepcount = 0
        maxtextheight = 0
        xcurr = self._OFFSET_X_DOC
        doc_y = plane_height + self._OFFSET_Y_DOC
        evidence_rows_starts = [doc_y]
        max_evidences_per_row = int(int(bounds_width) / self._OFFSET_DOC_TAB)
        for _, evidence in self._process_evidences.items():
            stepcount += 1
            evid_name = evidence[self._PROCESS_EVIDENCE_DESCR_KEY]
            if evid_name is not None:
                # Calculate rows of the description
                chars = len(evid_name)
                divisor = int(
                    self._WIDTH_LABEL_VARIANT_2 / self._DIVISOR_EVIDENCES_ROWS)
                rows = int(chars / divisor)
                textheight = int(rows * self._MULTIPLIER_EVIDENCES_TEXT_HEIGHT)
                if textheight > maxtextheight:
                    maxtextheight = textheight
                bpmn_shape = etree.SubElement(
                    bpmn_plane, self._ns.bpmndi + self._SHAPE_SUFFIX,
                    id=self._DATA_OBJECT_REFERENCE_PREFIX + str(
                        stepcount) + self._DI_SUFFIX,
                    bpmnElement=self._DATA_OBJECT_REFERENCE_PREFIX + str(
                        stepcount),
                    nsmap=self._ns.NSMAP)
                etree.SubElement(
                    bpmn_shape, self._ns.dc + self._BOUNDS_SUFFIX,
                    x=str(xcurr + self._OFFSET_DOC_TAB),
                    y=str(evidence_rows_starts[-1]),
                    width=str(self._WIDTH_DOC_ICON),
                    height=str(self._HEIGHT_DOC_ICON), nsmap=self._ns.NSMAP)
                bpmn_label = etree.SubElement(
                    bpmn_shape, self._ns.bpmndi + self._LABEL_SUFFIX,
                    nsmap=self._ns.NSMAP)
                y_pos = str(
                    evidence_rows_starts[-1] + self._OFFSET_EVIDENCES_Y_LABEL)
                etree.SubElement(
                    bpmn_label, self._ns.dc + self._BOUNDS_SUFFIX,
                    x=str(round(xcurr + self._OFFSET_DOC_TAB / 2)),
                    y=y_pos,
                    width=str(self._WIDTH_LABEL_VARIANT_2),
                    height=str(self._HEIGHT_LABEL),
                    nsmap=self._ns.NSMAP)
                xcurr += self._OFFSET_DOC_TAB
            # row is full no so continue to next row
            if max_evidences_per_row>0 and stepcount % max_evidences_per_row == 0:
                evidence_rows_start = evidence_rows_starts[-1] + \
                                      maxtextheight + 2 * self._HEIGHT_DOC_ICON + \
                                      self._OFFSET_X_DOC
                evidence_rows_starts.append(evidence_rows_start)
                maxtextheight = 0
                xcurr = self._OFFSET_X_DOC
        return xcurr, evidence_rows_starts[-1] + maxtextheight

    def _append_flow(self, definition, process_name):
        # Add the generic shapes (the flow etc.)
        bpmn_diagram = etree.SubElement(
            definition, self._ns.bpmndi + self._DIAGRAM_SUFFIX,
            id=self._TRISOTECH_ID_6,
            nsmap=self._ns.NSMAP)
        bpmn_diagram.attrib[QName(self._ns.di_NAMESPACE, self._NAME_KEY)
        ] = self._NAME_ATTR_PREFIX + process_name
        bpmn_diagram.attrib[QName(
            self._ns.di_NAMESPACE,
            self._DOCUMENTATION_KEY)] = self._DOCUMENTATION_ATTR
        bpmn_diagram.attrib[QName(self._ns.di_NAMESPACE, self._RESOLUTION_KEY)
        ] = self._RESOLUTION_ATTR
        bpmn_diagram.attrib[QName(
            self._ns.xsi_NAMESPACE, self._TYPE_KEY)] = self._TYPE_ATTR
        bpmn_plane = etree.SubElement(
            bpmn_diagram, self._ns.bpmndi + self._PLANE_SUFFIX,
            bpmnElement=self._C_PREFIX + str(hash(process_name)),
            nsmap=self._ns.NSMAP)
        bpmn_shape = etree.SubElement(
            bpmn_plane, self._ns.bpmndi + self._SHAPE_SUFFIX,
            id=self._TRISOTECH_ID + self._PARTICIPANT_PREFIX + str(
                hash(process_name)),
            bpmnElement=self._PARTICIPANT_PREFIX + str(hash(process_name)),
            isHorizontal=self._IS_HORIZONTAL_TRUE,
            nsmap=self._ns.NSMAP)
        # Now add the shapes for the main flow
        plane_height, xcurr = self._append_shapes_and_edges(bpmn_plane)
        bounds_width = xcurr + self._WIDTH_START_EVENT + self._WIDTH_ARROW + \
                       self._OFFSET_BOUNDS_WIDTH
        etree.SubElement(
            bpmn_shape, self._ns.dc + self._BOUNDS_SUFFIX,
            x=str(self._X_SHAPE),
            y=str(self._Y_SHAPE_VARIANT_3),
            width=str(bounds_width),
            height=str(plane_height),
            nsmap=self._ns.NSMAP)
        etree.SubElement(bpmn_shape, self._ns.bpmndi + self._LABEL_SUFFIX, )
        return bpmn_plane, plane_height, bounds_width

    def xml(self, data):
        root = etree.Element(self._DEFINITIONS_KEY)
        root.append(etree.Element(self._PROCESS_STR))
        semantic_element = etree.Element(
            f'{{{self._NAMESPACE[self._SEMANTIC_KEY]}}}{_SEMANTIC_STR}')
        etree.SubElement(
            semantic_element,
            f'{{{self._NAMESPACE[self._SEMANTIC_KEY]}}}{_DEFINITIONS_STR}')
        process_name = data.get(self._NAME_KEY)
        definition_element = etree.Element(
            self._ns.semantic + self._DEFINITIONS_KEY,
            id='_' + str(hash(process_name)),
            targetNamespace=self._NAMESPACE[self._XML_TARGET_KEY],
            nsmap=self._ns.NSMAP)
        # Read steps in order
        self._process_steps = {}
        stringsorted = data.get(self._FIELDS_KEY).get(self._PROCESS_STEPS_STR)
        if stringsorted is not None:
            integerkeyed = {int(k): v for k, v in stringsorted.items()}
            self._process_steps = OrderedDict(
                sorted(integerkeyed.items(), key=lambda t: t[0]))
            # Read evidences in order

        self._process_evidences = {}
        ev_stringsorted = data.get(self._FIELDS_KEY).get(
            self._PROCESS_EVIDENCES_STR)
        if ev_stringsorted is not None:
            ev_integerkeyed = {int(k): v for k, v in ev_stringsorted.items()}
            self._process_evidences = OrderedDict(
                sorted(ev_integerkeyed.items(), key=lambda t: t[0]))

        if self._process_steps is None:
            xml_string = ''
        else:
            process = self._append_process_tree(definition_element, process_name)
            self._append_data_objects(process)
            self._append_collaboration(definition_element, process_name)
            bpmn_plane, plane_height, bounds_width \
                = self._append_flow(definition_element, process_name)
            x_doc_max, y_doc_max \
                = self._append_data_object_shapes(bpmn_plane, plane_height, bounds_width)
            b_elems = bpmn_plane.findall(
                self._PLANE_FIND_ALL_QUERY, self._NAMESPACE)
            for b_elem in b_elems:
                b_elem.attrib[self._WIDTH_KEY] = str(
                    max(x_doc_max, int(b_elem.attrib[self._WIDTH_KEY])))
                b_elem.attrib[self._HEIGHT_KEY] = str(y_doc_max)
            dom = xml.dom.minidom.parseString(etree.tostring(
                definition_element, encoding='UTF-8', xml_declaration=True))
            xml_string = dom.toprettyxml()
        return xml_string
