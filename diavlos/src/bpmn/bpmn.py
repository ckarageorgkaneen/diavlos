from collections import OrderedDict
import xml.dom.minidom
from lxml import etree
from lxml.etree import QName

_DIGITAL_STR = 'digital'
_TITLE_STR = 'title'
_IMPLEMENTATION_STR = 'implementation'
_CHILD_STR = 'child'
_SEMANTIC_STR = 'semantic'
_DEFINITIONS_STR = 'definitions'
_TIMER_STR = 'Timer'
_MIN_STR = 'min'
_MAX_STR = 'max'
_NUM_ID_SUFFIX = 'num_id'
_PREV_CHILD_SUFFIX = f'previous_{_CHILD_STR}'

_MAX_DURATION_TEMPLATE = {
    'Λεπτά': 'PT{}M',
    'Ώρες': 'PT{}Η',
    'Ημέρες': 'P{}DS',
    'Εβδομάδες': 'P{}WS',
    'Μήνες': 'P{}MS'
}


def bracketize(string):
    return f'{{{string}}}'


def getMaxDurationAsString(timer):
    duration_type = timer[2]
    try:
        template = _MAX_DURATION_TEMPLATE[duration_type]
    except KeyError:
        return ''
    max_duration = timer[1]
    min_duration = timer[0]
    out=max(int(max_duration),int(min_duration))
    return template.format(out)


class BPMNNamespaces:
    def __init__(self, semantic, bpmndi, di, dc, xsi, NSMAP, di_NAMESPACE,
                 xsi_NAMESPACE):
        self.semantic = semantic
        self.bpmndi = bpmndi
        self.di = di
        self.dc = dc
        self.xsi = xsi
        self.NSMAP = NSMAP
        self.di_NAMESPACE = di_NAMESPACE
        self.xsi_NAMESPACE = xsi_NAMESPACE


class BPMN:
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
    _OFFSET_DOC_TAB = 200
    _OFFSET_X_DOC = 100
    _OFFSET_Y_DOC = 150
    _OFFSET_EVIDENCES_Y_LABEL = 60
    _OFFSET_BOUNDS_WIDTH = 50
    # Multipliers
    _MULTIPLIER_BOX_HEIGHT = 120
    _MULTIPLIER_TASK_TEXT_HEIGHT = 27
    _MULTIPLIER_EVIDENCES_TEXT_HEIGHT = 10
    # Divisors
    _DIVISOR_BOX_HEIGHT = 25
    _DIVISOR_TASK_ROWS = 9
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
        self._PROCESS_STEP_IMPLEMENTATION = \
            f'{process_step_prefix}_{_IMPLEMENTATION_STR}'
        self._PROCESS_STEP_NUM_ID = f'{process_step_prefix}_{_NUM_ID_SUFFIX}'
        self._PROCESS_STEP_CHILD = f'{process_step_prefix}_{_CHILD_STR}'
        self._PROCESS_STEP_PREVIOUS_CHILD = f'{process_step_prefix}_'\
            f'{_PREV_CHILD_SUFFIX}'

        self._ns = BPMNNamespaces(
            semantic=bracketize(self._NAMESPACE[self._SEMANTIC_KEY]),
            bpmndi=bracketize(self._NAMESPACE[self._BPMNDI_KEY]),
            di=bracketize(self._NAMESPACE[self._DI_KEY]),
            dc=bracketize(self._NAMESPACE[self._DC_KEY]),
            xsi=bracketize(self._NAMESPACE[self._XSI_KEY]),
            NSMAP=self._NAMESPACE,
            di_NAMESPACE=self._NAMESPACE[self._DI_KEY],
            xsi_NAMESPACE=self._NAMESPACE[self._XSI_KEY])
        self._process_steps = None

    def group_options(self, opts):
        chains = {}
        for n in opts:
            curr = n.get(self._PROCESS_STEP_NUM_ID)
            prev = n.get(self._PROCESS_STEP_PREVIOUS_CHILD)
            if chains.get(prev) is not None:
                arr = chains.get(prev)
                arr.append(n)
                chains.pop(prev, None)
                chains[curr] = arr
            else:
                arr = []
                arr.append(n)
                chains[curr] = arr
        maxchainlength = 0
        for k in chains:
            if len(chains.get(k)) > maxchainlength:
                maxchainlength = len(chains.get(k))
        return chains, maxchainlength

    def _create_waypoint(self, BPMNEdge, x, y):
        waypoint = etree.SubElement(
            BPMNEdge,
            self._ns.di + self._WAYPOINT_SUFFIX,
            x=str(x),
            y=str(y),
            nsmap=self._ns.NSMAP)
        return waypoint

    def _appendStartEventTree(self, process, allnodes):
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

    def _appendDataObjects(self, definition, process, data):
        stepcount = 0
        # Parse the Evidences and add a dataObject and a dataObjectReference
        # for each
        for evidence_num, evidence in self._process_evidences.items():
            stepcount += 1
            evid_name = evidence[self._PROCESS_EVIDENCE_DESCR_KEY]
            if evid_name is not None:
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

    def _appendEndNodes(self, data, process, allnodes, options, stepcount):
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

    def _appendProcessTree(self, definition, process_name, data):
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
        self._appendStartEventTree(process, allnodes)
        # Parse the process steps and either add plainEventNodes, or
        # put the branchNodes in a list and handle them when the first
        # plainEventNode appears
        for step_num, step in self._process_steps.items():
            stepcount += 1
            if step.get(self._PROCESS_STEP_TITLE) is not None:
                if step.get(self._PROCESS_STEP_CHILD) == \
                        self._PROCESS_STEP_CHILD_YES:
                    options.append(step)
                    allnodes.append(self._SUBTASK_PREFIX + str(stepcount))
                    branched = True
                else:
                    self._handlePlainNodes(data, process, allnodes, options,
                                           stepcount)
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
        # Add a default endEvent
        self._appendEndNodes(data, process, allnodes, options, stepcount)
        return process

    def _handlePlainNodes(self, data, process, allnodes, options, stepcount):
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
        if self._PROCESS_STEPS_STR==self._PROCESS_STEPS_DIGITAL_STR:
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
            boundaryEvent = etree.SubElement(
                process, self._ns.semantic + self._BOUNDARY_EVENT_SUFFIX,
                id=self._TIMER_PREFIX + str(stepcount),
                # name=self._TASK_PREFIX + str(stepcount)+"_Duration",
                name=name,
                attachedToRef=self._TASK_PREFIX + str(stepcount),
                nsmap=self._ns.NSMAP)
            timerEvent = etree.SubElement(
                boundaryEvent,
                self._ns.semantic + self._TIMER_EVENT_DEF_SUFFIX)
            timeDuration = etree.SubElement(
                timerEvent, self._ns.semantic + self._TIME_DURATION_SUFFIX)
            timeDuration.attrib[
                QName(self._ns.xsi_NAMESPACE, self._TYPE_KEY)] = \
                _SEMANTIC_STR + ':' + self._TFORMALEXPRESSION
            timeDuration.text = getMaxDurationAsString(timer)
            incoming = etree.SubElement(
                task, self._ns.semantic + self._INCOMING_SUFFIX,
                nsmap=self._ns.NSMAP)
            incoming.text = self._SEQUENCE_FLOW_PREFIX + str(stepcount - 1)
            outgoing = etree.SubElement(
                task, self._ns.semantic + self._OUTGOING_SUFFIX,
                nsmap=self._ns.NSMAP)
            outgoing.text = self._SEQUENCE_FLOW_PREFIX + str(stepcount)
        # If there BranchNodes are found from the previous event
        else:
            chains, maxchainlength = self.group_options(options)
            self._addBranchNodes(options, chains, process, allnodes, stepcount)
            self._addMergeNodes(options, chains, process,
                                allnodes, stepcount, stepname,
                                steptype, timer, False)
            options = []

    def _appendCollaboration(self, definition, process_name):
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

    def _addBranchNodes(self, options, chains, process, allnodes, stepcount):
        # Add an exclusiveGateway node, with an incoming edge
        exclusiveGateway = etree.SubElement(
            process, self._ns.semantic + self._EXCLUSIVE_GATEWAY_SUFFIX,
            id=self._EXCLUSIVE_GATEWAY_PREFIX + str(stepcount - len(options)),
            name=self._SELECTION_NAME, nsmap=self._ns.NSMAP)
        incoming = etree.SubElement(
            exclusiveGateway,
            self._ns.semantic + self._INCOMING_SUFFIX,
            nsmap=self._ns.NSMAP)
        incoming.text = self._SEQUENCE_FLOW_PREFIX + \
            str(stepcount - len(options) - 1)
        # Add a sequenceFlow for the exclusiveGateway's incoming edge
        etree.SubElement(
            process, self._ns.semantic + self._SEQUENCE_FLOW_SUFFIX,
            id=self._SEQUENCE_FLOW_PREFIX + str(stepcount - len(options) - 1),
            sourceRef=allnodes[stepcount - len(options) - 1],
            targetRef=self._EXCLUSIVE_GATEWAY_PREFIX + str(
                stepcount - len(options)),
            nsmap=self._ns.NSMAP)
        # Add:
        # i) the outgoing edges
        # ii) the sequenceFlows for the outgoing edges,
        # iii) the subtasks,
        # iv) their incoming and outgoing edges,
        # v) the respective SequenceFlows for these edges
        subchaincount = 0
        for key in chains:
            chain = chains.get(key)
            subchaincount += 1
            #  Handle the 1st node of each chain
            step = chain[0]

            stepimpl = step.get(self._PROCESS_STEP_IMPLEMENTATION)
            if stepimpl == self._MANUAL_TASK:
                steptype = self._MANUAL_TASK_SUFFIX
            elif stepimpl == self._SERVICE_TASK:
                steptype = self._SERVICE_TASK_SUFFIX
            else:
                steptype = self._TASK_SUFFIX

            if self._PROCESS_STEPS_STR==self._PROCESS_STEPS_DIGITAL_STR:
              timer = (step.get(self._PROCESS_STEP_DIGITAL_DURATION_MIN),
                    step.get(self._PROCESS_STEP_DIGITAL_DURATION_MAX),
                    step.get(self._PROCESS_STEP_DIGITAL_DURATION_TYPE))
            else:
              timer = (step.get(self._PROCESS_STEP_DURATION_MIN),
                    step.get(self._PROCESS_STEP_DURATION_MAX),
                    step.get(self._PROCESS_STEP_DURATION_TYPE))

            # i)
            outgoing = etree.SubElement(
                exclusiveGateway,
                self._ns.semantic + self._OUTGOING_SUFFIX,
                nsmap=self._ns.NSMAP)
            # ii)  e.g. SequenceFlow_3_1_1, SequenceFlow_3_2_1  etc.
            outgoing.text = self._SEQUENCE_FLOW_PREFIX + \
                str(stepcount - len(options)) + '_' + str(
                    subchaincount) + self._1_SUFFIX
            # iii) e.g. Subtask_3_1_1, Subtask_3_2_1  etc.
            subTask = etree.SubElement(
                process, self._ns.semantic + steptype,
                id=self._SUBTASK_PREFIX + str(
                    stepcount - len(options)) + '_' + str(
                    subchaincount) + self._1_SUFFIX,
                name=step.get(self._PROCESS_STEP_TITLE),
                nsmap=self._ns.NSMAP)
            name = f'{_MIN_STR}:{timer[0]}, {_MAX_STR}:{timer[1]} {timer[2]}'
            boundaryEvent = etree.SubElement(
                process, self._ns.semantic + self._BOUNDARY_EVENT_SUFFIX,
                id=self._TIMER_PREFIX + str(
                    stepcount - len(options)) + '_' + str(
                    subchaincount) + self._1_SUFFIX,
                # name=self._TASK_PREFIX + str(stepcount)+"_Duration",
                name=name,
                attachedToRef=self._SUBTASK_PREFIX + str(
                    stepcount - len(options)) + '_' + str(
                    subchaincount) + self._1_SUFFIX,
                nsmap=self._ns.NSMAP)
            timerEvent = etree.SubElement(
                boundaryEvent,
                self._ns.semantic + self._TIMER_EVENT_DEF_SUFFIX)
            timeDuration = etree.SubElement(
                timerEvent, self._ns.semantic + self._TIME_DURATION_SUFFIX)
            timeDuration.attrib[
                QName(self._ns.xsi_NAMESPACE, self._TYPE_KEY)] = \
                _SEMANTIC_STR + ':' + self._TFORMALEXPRESSION
            timeDuration.text = getMaxDurationAsString(timer)
            # Set the current task as the last task of the chain
            lastTask = subTask
            # iv)
            incoming = etree.SubElement(
                subTask, self._ns.semantic + self._INCOMING_SUFFIX,
                nsmap=self._ns.NSMAP)
            incoming.text = self._SEQUENCE_FLOW_PREFIX + \
                str(stepcount - len(options)) + '_' + \
                str(subchaincount) + '_' + str(1)
            etree.SubElement(
                process,
                self._ns.semantic + self._SEQUENCE_FLOW_SUFFIX,
                id=self._SEQUENCE_FLOW_PREFIX + str(
                    stepcount - len(options)) + '_' + str(
                    subchaincount) + self._1_SUFFIX,
                sourceRef=self._EXCLUSIVE_GATEWAY_PREFIX + str(
                    stepcount - len(options)),
                targetRef=self._SUBTASK_PREFIX + str(
                    stepcount - len(options)) + '_' + str(
                    subchaincount) + self._1_SUFFIX, nsmap=self._ns.NSMAP)
            if (len(chain) > 1):
                lastTask = self._add_chain_nodes(
                    options, chain, process, stepcount, subchaincount,
                    lastTask)
            # In all cases
            outgoing = etree.SubElement(
                lastTask, self._ns.semantic + self._OUTGOING_SUFFIX,
                nsmap=self._ns.NSMAP)
            outgoing.text = self._SEQUENCE_FLOW_PREFIX + \
                str(stepcount - len(options) + 1) + \
                '_' + str(subchaincount) + self._LAST_SUFFIX

    def _add_chain_nodes(self, options, chain, process, stepcount,
                         subchaincount, lastTask):
        """This method adds the remaining nodes of a chain.
        If the case has more than one step
        """
        substepcount = 1
        for step in chain[1:]:
            stepimpl = step.get(self._PROCESS_STEP_IMPLEMENTATION)
            if stepimpl == self._MANUAL_TASK:
                steptype = self._MANUAL_TASK_SUFFIX
            elif stepimpl == self._SERVICE_TASK:
                steptype = self._SERVICE_TASK_SUFFIX
            else:
                steptype = self._TASK_SUFFIX
            timer = (step.get(self._PROCESS_STEP_DURATION_MIN),
                     step.get(self._PROCESS_STEP_DURATION_MAX),
                     step.get(self._PROCESS_STEP_DURATION_TYPE))
            substepcount += 1
            curr_id = str(stepcount - len(options)) + '_' + \
                str(subchaincount) + '_' + str(substepcount)
            prev_id = str(stepcount - len(options)) + '_' + \
                str(subchaincount) + '_' + str(substepcount - 1)
            subTask = etree.SubElement(
                process, self._ns.semantic + steptype,
                id=self._SUBTASK_PREFIX + curr_id,
                name=step.get(self._PROCESS_STEP_TITLE),
                nsmap=self._ns.NSMAP)
            outgoing = etree.SubElement(
                lastTask, self._ns.semantic + self._OUTGOING_SUFFIX,
                nsmap=self._ns.NSMAP)
            outgoing.text = self._SEQUENCE_FLOW_PREFIX + curr_id
            incoming = etree.SubElement(
                subTask, self._ns.semantic + self._INCOMING_SUFFIX,
                nsmap=self._ns.NSMAP)
            incoming.text = self._SEQUENCE_FLOW_PREFIX + curr_id
            etree.SubElement(process,
                             self._ns.semantic + self._SEQUENCE_FLOW_SUFFIX,
                             id=self._SEQUENCE_FLOW_PREFIX + curr_id,
                             sourceRef=self._SUBTASK_PREFIX + prev_id,
                             targetRef=self._SUBTASK_PREFIX + curr_id,
                             nsmap=self._ns.NSMAP)
            name = f'{_MIN_STR}:{timer[0]}, {_MAX_STR}:{timer[1]} {timer[2]}'
            boundaryEvent = etree.SubElement(
                process, self._ns.semantic + self._BOUNDARY_EVENT_SUFFIX,
                id=self._TIMER_PREFIX + curr_id,
                # name=self._TASK_PREFIX + str(stepcount)+"_Duration",
                name=name,
                attachedToRef=self._SUBTASK_PREFIX + curr_id,
                nsmap=self._ns.NSMAP)
            timerEvent = etree.SubElement(
                boundaryEvent,
                self._ns.semantic + self._TIMER_EVENT_DEF_SUFFIX)
            timeDuration = etree.SubElement(
                timerEvent, self._ns.semantic + self._TIME_DURATION_SUFFIX)
            timeDuration.attrib[
                QName(self._ns.xsi_NAMESPACE, self._TYPE_KEY)] = \
                _SEMANTIC_STR + ':' + self._TFORMALEXPRESSION
            timeDuration.text = getMaxDurationAsString(timer)
            # Set this task as the lastTask so that it can used in the next
            # iteration as the previous node
            lastTask = subTask
        return lastTask

    def _addMergeNodes(self, options, chains, process, allnodes, stepcount,
                       stepname, steptype, timer, isEndNode):
        task = etree.SubElement(process, self._ns.semantic + steptype,
                                id=self._TASK_PREFIX + str(stepcount),
                                name=stepname, nsmap=self._ns.NSMAP)
        subchaincount = 0
        outgoing = etree.SubElement(
            task, self._ns.semantic + self._OUTGOING_SUFFIX,
            nsmap=self._ns.NSMAP)
        outgoing.text = self._SEQUENCE_FLOW_PREFIX + str(stepcount)
        name = f'{_MIN_STR}:{timer[0]}, {_MAX_STR}:{timer[1]} {timer[2]}'
        boundaryEvent = etree.SubElement(
            process, self._ns.semantic + self._BOUNDARY_EVENT_SUFFIX,
            id=self._TIMER_PREFIX + str(stepcount),
            # name=self._TASK_PREFIX + str(stepcount)+"_Duration",
            name=name,
            attachedToRef=self._TASK_PREFIX + str(stepcount),
            nsmap=self._ns.NSMAP)
        timerEvent = etree.SubElement(
            boundaryEvent, self._ns.semantic + self._TIMER_EVENT_DEF_SUFFIX)
        timeDuration = etree.SubElement(
            timerEvent, self._ns.semantic + self._TIME_DURATION_SUFFIX)
        timeDuration.attrib[
            QName(self._ns.xsi_NAMESPACE, self._TYPE_KEY)] = \
            _SEMANTIC_STR + ':' + self._TFORMALEXPRESSION
        timeDuration.text = getMaxDurationAsString(timer)
        for k in chains:
            chain = chains.get(k)
            subchaincount += 1
            incoming = etree.SubElement(
                task, self._ns.semantic + self._INCOMING_SUFFIX,
                nsmap=self._ns.NSMAP)
            incoming.text = self._SEQUENCE_FLOW_PREFIX + \
                str(stepcount - len(options) + 1) + \
                '_' + str(subchaincount) + self._LAST_SUFFIX
            # Append the SequenceFlows for the merge
            # (but maybe it is better to move it to the merge)
            etree.SubElement(process,
                             self._ns.semantic + self._SEQUENCE_FLOW_SUFFIX,
                             id=self._SEQUENCE_FLOW_PREFIX + str(
                                 stepcount - len(options) + 1) + '_' + str(
                                 subchaincount) + self._LAST_SUFFIX,
                             sourceRef=self._SUBTASK_PREFIX + str(
                                 stepcount - len(options)) + '_' + str(
                                 subchaincount) + '_' + str(len(chain)),
                             targetRef=self._TASK_PREFIX + str(stepcount),
                             nsmap=self._ns.NSMAP)

    def _getChainHeights(self, options, chains, stepcount, offset):
        subchaincount = 0
        chainHeights = []
        for k in chains:
            steps = chains.get(k)
            step = steps[0]
            maxChainHeight = 0
            stepname = step.get(self._PROCESS_STEP_TITLE)
            rows = int(len(stepname) / self._DIVISOR_TASK_ROWS)
            rounded_height = int(self._MULTIPLIER_TASK_TEXT_HEIGHT * rows)
            subchaincount += 1
            if len(steps) > 1:
                substepcount = 1
                for step in steps[1:]:
                    substepcount += 1
                    stepname = step.get(self._PROCESS_STEP_TITLE)
                    rows = int(len(stepname) / self._DIVISOR_TASK_ROWS)
                    rounded_height = int(
                        self._MULTIPLIER_TASK_TEXT_HEIGHT * rows)
                    if rounded_height > maxChainHeight:
                        maxChainHeight = rounded_height
            else:
                stepname = step.get(self._PROCESS_STEP_TITLE)
                rows = int(len(stepname) / self._DIVISOR_TASK_ROWS)
                rounded_height = int(self._MULTIPLIER_TASK_TEXT_HEIGHT * rows)
                maxChainHeight = rounded_height

            chainHeights.append(maxChainHeight)
        return chainHeights

    def _addBranchNodeShapes(self, options, chains, BPMNPlane, stepcount,
                             offset, xcurr):
        chainHeights = self._getChainHeights(
            options, chains, stepcount, offset)
        # Add the ExclusiveGateway shape
        mainflownodes = stepcount - len(options)
        BPMNShape = etree.SubElement(
            BPMNPlane, self._ns.bpmndi + self._SHAPE_SUFFIX,
            id=self._EXCLUSIVE_GATEWAY_PREFIX + str(
                mainflownodes) + self._DI_SUFFIX,
            bpmnElement=self._EXCLUSIVE_GATEWAY_PREFIX + str(mainflownodes),
            isMarkerVisible=self._IS_MARKER_VISIBLE_TRUE, nsmap=self._ns.NSMAP)
        etree.SubElement(
            BPMNShape, self._ns.dc + self._BOUNDS_SUFFIX,
            x=str(xcurr + self._WIDTH_ARROW),
            y=str(self._Y_SHAPE),
            width=str(self._WIDTH_RHOMBUS),
            height=str(self._HEIGHT_RHOMBUS),
            nsmap=self._ns.NSMAP)
        BPMNLabel = etree.SubElement(
            BPMNShape, self._ns.bpmndi + self._LABEL_SUFFIX,
            nsmap=self._ns.NSMAP)
        etree.SubElement(BPMNLabel, self._ns.dc + self._BOUNDS_SUFFIX,
                         x=str(xcurr + self._OFFSET_BOUNDS),
                         y=str(self._Y_LABEL_VARIANT),
                         width=str(self._WIDTH_LABEL_VARIANT),
                         height=str(self._HEIGHT_LABEL_VARIANT),
                         nsmap=self._ns.NSMAP)
        # Check if the previous flow node is the StartEvent or a simple Task
        head = self._TASK_PREFIX
        if stepcount == 2:
            head = self._START_EVENT_PREFIX
        # Draw an edge from the previous node to the ExclusiveGateway node
        BPMNEdge = etree.SubElement(
            BPMNPlane, self._ns.bpmndi + self._EDGE_SUFFIX,
            id=self._SEQUENCE_FLOW_PREFIX + str(
                mainflownodes - 1) + self._DI_SUFFIX,
            bpmnElement=self._SEQUENCE_FLOW_PREFIX + str(mainflownodes - 1),
            sourceElement=head + str(stepcount - 1 - len(options)),
            targetElement=self._EXCLUSIVE_GATEWAY_PREFIX + str(mainflownodes),
            nsmap=self._ns.NSMAP)
        self._create_waypoint(
            BPMNEdge, xcurr, self._Y_START)
        self._create_waypoint(
            BPMNEdge, xcurr + self._WIDTH_ARROW, self._Y_START)

        BPMNLabel = etree.SubElement(
            BPMNEdge, self._ns.bpmndi + self._LABEL_SUFFIX,
            nsmap=self._ns.NSMAP)
        etree.SubElement(
            BPMNLabel, self._ns.dc + self._BOUNDS_SUFFIX,
            x=str(round((xcurr + self._WIDTH_ARROW) / 2)),
            y=str(self._Y_LABEL),
            width=str(self._WIDTH_LABEL),
            height=str(self._HEIGHT_LABEL),
            nsmap=self._ns.NSMAP)
        subchaincount = 0
        ymove = 0
        xstart = xcurr + self._WIDTH_ARROW + self._WIDTH_RHOMBUS
        xend = xstart + self._WIDTH_ARROW
        maxChainLength = 1
        gap = self._HEIGHT_LABEL

        for k in chains:
            steps = chains.get(k)
            step = steps[0]
            subchaincount += 1
            stepname = step.get(self._PROCESS_STEP_TITLE)
            rows = int(len(stepname) / self._DIVISOR_TASK_ROWS)
            rounded_height = int(self._MULTIPLIER_TASK_TEXT_HEIGHT * rows)
            BPMNShape = etree.SubElement(
                BPMNPlane, self._ns.bpmndi + self._SHAPE_SUFFIX,
                id=self._SUBTASK_PREFIX + str(
                    mainflownodes) + '_' + str(
                    subchaincount) + self._1_DI_SUFFIX,
                bpmnElement=self._SUBTASK_PREFIX + str(
                    mainflownodes) + '_' + str(subchaincount) + self._1_SUFFIX,
                nsmap=self._ns.NSMAP)
            etree.SubElement(
                BPMNShape, self._ns.dc + self._BOUNDS_SUFFIX,
                x=str(xend),
                y=str(self._Y_SHAPE + ymove),
                width=str(self._WIDTH_TASK),
                # height=str(round(
                #   self._MULTIPLIER_BOX_HEIGHT * boxHeightFactor)),
                height=str(rounded_height),
                nsmap=self._ns.NSMAP)
            if subchaincount == 1:
                BPMNEdge = etree.SubElement(
                    BPMNPlane, self._ns.bpmndi + self._EDGE_SUFFIX,
                    id=self._SEQUENCE_FLOW_PREFIX + str(
                        mainflownodes) + '_' + str(
                        subchaincount) + self._1_DI_SUFFIX,
                    bpmnElement=self._SEQUENCE_FLOW_PREFIX + str(
                        mainflownodes) + '_' + str(
                        subchaincount) + self._1_SUFFIX,
                    sourceElement=self._EXCLUSIVE_GATEWAY_PREFIX + str(
                        mainflownodes),
                    targetElement=self._SUBTASK_PREFIX + str(
                        mainflownodes) + '_' + str(
                        subchaincount) + self._1_SUFFIX,
                    nsmap=self._ns.NSMAP)
                self._create_waypoint(BPMNEdge, xstart, self._Y_START)
                self._create_waypoint(BPMNEdge, xend, self._Y_START)
                BPMNLabel = etree.SubElement(
                    BPMNEdge,
                    self._ns.bpmndi + self._LABEL_SUFFIX,
                    nsmap=self._ns.NSMAP)
                etree.SubElement(BPMNLabel, self._ns.dc + self._BOUNDS_SUFFIX,
                                 x=str(round(xend + xstart / 2)),
                                 y=str(self._Y_LABEL),
                                 width=str(self._WIDTH_LABEL),
                                 height=str(self._HEIGHT_LABEL),
                                 nsmap=self._ns.NSMAP)

                # add timer icon in first branched node first line
                id_ = f'{self._SUBTASK_PREFIX}{mainflownodes}_' \
                      f'{subchaincount}_1_Timer_{mainflownodes}_' \
                      f'{subchaincount}_1'
                BPMNShape = etree.SubElement(
                    BPMNPlane, self._ns.bpmndi + self._SHAPE_SUFFIX,
                    id=id_,
                    bpmnElement=self._TIMER_PREFIX + str(
                        mainflownodes) + '_' + str(subchaincount) + '_1',
                    nsmap=self._ns.NSMAP)
                etree.SubElement(
                    BPMNShape, self._ns.dc + self._BOUNDS_SUFFIX,
                    x=str(xend + self._TASK_WIDTH - 15),
                    y=str(self._Y_LABEL_VARIANT + rounded_height + 10),
                    width=str(32),
                    height=str(32),
                    nsmap=self._ns.NSMAP)
                BPMNLabel = etree.SubElement(
                    BPMNShape, self._ns.bpmndi + self._LABEL_SUFFIX,
                    nsmap=self._ns.NSMAP)
                y = str(self._Y_LABEL_VARIANT + rounded_height + 32)
                etree.SubElement(BPMNLabel, self._ns.dc + self._BOUNDS_SUFFIX,
                                 x=str(xend + 30),
                                 y=y,
                                 width=str(self._WIDTH_LABEL_VARIANT),
                                 height=str(self._HEIGHT_LABEL_VARIANT),
                                 nsmap=self._ns.NSMAP)
            else:
                BPMNEdge = etree.SubElement(
                    BPMNPlane, self._ns.bpmndi + self._EDGE_SUFFIX,
                    id=self._SEQUENCE_FLOW_PREFIX + str(
                        mainflownodes) + '_' + str(
                        subchaincount) + self._1_DI_SUFFIX,
                    bpmnElement=self._SEQUENCE_FLOW_PREFIX + str(
                        mainflownodes) + '_' + str(
                        subchaincount) + self._1_SUFFIX,
                    sourceElement=self._EXCLUSIVE_GATEWAY_PREFIX + str(
                        mainflownodes),
                    targetElement=self._SUBTASK_PREFIX + str(
                        mainflownodes) + '_' + str(
                        subchaincount) + self._1_SUFFIX,
                    nsmap=self._ns.NSMAP)
                self._create_waypoint(BPMNEdge, xstart, self._Y_START)
                self._create_waypoint(
                    BPMNEdge, xstart, self._Y_START + ymove)
                self._create_waypoint(
                    BPMNEdge, xend, self._Y_START + ymove)
                BPMNLabel = etree.SubElement(
                    BPMNEdge, self._ns.bpmndi + self._LABEL_SUFFIX,
                    nsmap=self._ns.NSMAP)
                etree.SubElement(
                    BPMNLabel, self._ns.dc + self._BOUNDS_SUFFIX,
                    x=str(round(xend + xstart / 2)),
                    y=str(self._Y_LABEL + ymove),
                    width=str(self._WIDTH_LABEL),
                    height=str(self._HEIGHT_LABEL),
                    nsmap=self._ns.NSMAP)

                # add timer icon in first branched node all other lines
                BPMNShape = etree.SubElement(
                    BPMNPlane, self._ns.bpmndi + self._SHAPE_SUFFIX,
                    id=self._SUBTASK_PREFIX + str(
                        mainflownodes) + '_' + str(
                        subchaincount) + '_1' + '_Timer_' + str(
                        mainflownodes) + '_' + str(
                        subchaincount) + '_1',
                    bpmnElement=self._TIMER_PREFIX + str(
                        mainflownodes) + '_' + str(
                        subchaincount) + '_1',
                    nsmap=self._ns.NSMAP)
                etree.SubElement(
                    BPMNShape, self._ns.dc + self._BOUNDS_SUFFIX,
                    x=str(xend + self._TASK_WIDTH - 15),
                    y=str(ymove + self._Y_LABEL_VARIANT + rounded_height + 10),
                    width=str(32),
                    height=str(32),
                    nsmap=self._ns.NSMAP)
                BPMNLabel = etree.SubElement(
                    BPMNShape, self._ns.bpmndi + self._LABEL_SUFFIX,
                    nsmap=self._ns.NSMAP)
                y = str(ymove + self._Y_LABEL_VARIANT + rounded_height + 32)
                etree.SubElement(BPMNLabel, self._ns.dc + self._BOUNDS_SUFFIX,
                                 x=str(xend + 30),
                                 y=y,
                                 width=str(self._WIDTH_LABEL_VARIANT),
                                 height=str(self._HEIGHT_LABEL_VARIANT),
                                 nsmap=self._ns.NSMAP)

            if len(steps) > 1:
                if len(steps) > maxChainLength:
                    maxChainLength = len(steps)
                substepcount = 1
                for step in steps[1:]:
                    substepcount += 1

                    stepname = step.get(self._PROCESS_STEP_TITLE)
                    rows = int(len(stepname) / self._DIVISOR_TASK_ROWS)
                    rounded_height = int(
                        self._MULTIPLIER_TASK_TEXT_HEIGHT * rows)

                    curr_subtask_id = str(mainflownodes) + '_' + \
                        str(subchaincount) + '_' + str(substepcount)
                    prev_subtask_id = str(mainflownodes) + '_' + \
                        str(subchaincount) + '_' + str(substepcount - 1)
                    bpmn_shape_id = self._SUBTASK_PREFIX + curr_subtask_id + \
                        self._DI_SUFFIX
                    BPMNShape = etree.SubElement(
                        BPMNPlane, self._ns.bpmndi + self._SHAPE_SUFFIX,
                        id=bpmn_shape_id,
                        bpmnElement=self._SUBTASK_PREFIX + curr_subtask_id,
                        nsmap=self._ns.NSMAP)
                    xnew = xstart + (self._WIDTH_ARROW + self._WIDTH_TASK) * \
                        (substepcount - 1)
                    xcurr = xnew + (self._WIDTH_ARROW + self._WIDTH_TASK)

                    etree.SubElement(
                        BPMNShape, self._ns.dc + self._BOUNDS_SUFFIX,
                        x=str(xnew + self._WIDTH_ARROW),
                        y=str(self._Y_SHAPE + ymove),
                        width=str(self._WIDTH_TASK),
                        height=str(rounded_height),
                        nsmap=self._ns.NSMAP)
                    bpmn_edge_id = self._SEQUENCE_FLOW_PREFIX + \
                        curr_subtask_id + self._DI_SUFFIX
                    bpmn_element = self._SEQUENCE_FLOW_PREFIX + curr_subtask_id
                    BPMNEdge = etree.SubElement(
                        BPMNPlane, self._ns.bpmndi + self._EDGE_SUFFIX,
                        id=bpmn_edge_id,
                        bpmnElement=bpmn_element,
                        sourceElement=self._SUBTASK_PREFIX + prev_subtask_id,
                        targetElement=self._SUBTASK_PREFIX + curr_subtask_id,
                        nsmap=self._ns.NSMAP)
                    self._create_waypoint(
                        BPMNEdge, xnew, self._Y_START + ymove)
                    self._create_waypoint(
                        BPMNEdge, xnew + self._WIDTH_ARROW,
                        self._Y_START + ymove)
                    BPMNLabel = etree.SubElement(
                        BPMNEdge, self._ns.bpmndi + self._LABEL_SUFFIX,
                        nsmap=self._ns.NSMAP)
                    etree.SubElement(
                        BPMNLabel, self._ns.dc + self._BOUNDS_SUFFIX,
                        x=str(round(xnew + self._WIDTH_ARROW / 2)),
                        y=str(self._Y_LABEL),
                        width=str(self._WIDTH_LABEL),
                        height=str(self._HEIGHT_LABEL),
                        nsmap=self._ns.NSMAP)
                    # Add timer icon in branched nodes
                    id_ = f'{self._SUBTASK_PREFIX}{curr_subtask_id}_Timer_' \
                          f'{curr_subtask_id}'
                    BPMNShape = etree.SubElement(
                        BPMNPlane, self._ns.bpmndi + self._SHAPE_SUFFIX,
                        id=id_,
                        bpmnElement=self._TIMER_PREFIX + curr_subtask_id,
                        nsmap=self._ns.NSMAP)
                    y = str(
                        ymove + self._Y_LABEL_VARIANT + rounded_height + 10)
                    etree.SubElement(
                        BPMNShape, self._ns.dc + self._BOUNDS_SUFFIX,
                        x=str(xcurr - 15),
                        y=y,
                        width=str(32),
                        height=str(32),
                        nsmap=self._ns.NSMAP)
                    BPMNLabel = etree.SubElement(
                        BPMNShape, self._ns.bpmndi + self._LABEL_SUFFIX,
                        nsmap=self._ns.NSMAP)
                    y = str(
                        ymove + self._Y_LABEL_VARIANT + rounded_height + 32)
                    etree.SubElement(BPMNLabel,
                                     self._ns.dc + self._BOUNDS_SUFFIX,
                                     x=str(xcurr - self._TASK_WIDTH + 30),
                                     y=y,
                                     width=str(self._WIDTH_LABEL_VARIANT),
                                     height=str(self._HEIGHT_LABEL_VARIANT),
                                     nsmap=self._ns.NSMAP)

            ymove += gap + chainHeights[subchaincount - 1]
        return ymove, chainHeights

    def _addMergeNodeShapes(self, options, chains, BPMNPlane, stepcount,
                            offset, chainHeights, maxBranchLength, xcurr,
                            rounded_height):
        gap = self._HEIGHT_LABEL
        head = self._TASK_PREFIX
        xstart = xcurr + self._WIDTH_ARROW + \
            self._WIDTH_RHOMBUS + (self._WIDTH_ARROW + self._WIDTH_TASK)
        mainflownodes = stepcount - len(options)
        ymove = 0
        subchaincount = 0
        for k in chains:
            chain = chains.get(k)
            subchaincount += 1
            currstart = xstart + (len(chain) - 1) * \
                (self._WIDTH_ARROW + self._WIDTH_TASK)
            xend = xstart + (maxBranchLength - 1) * \
                (self._WIDTH_ARROW + self._WIDTH_TASK) + 2 * self._WIDTH_ARROW
            xmid = round((currstart + xend) / 2)
            BPMNEdge = etree.SubElement(
                BPMNPlane, self._ns.bpmndi + self._EDGE_SUFFIX,
                id=self._SEQUENCE_FLOW_PREFIX + str(
                    mainflownodes + 1) + '_' + str(
                    subchaincount) + self._LAST_DI_SUFFIX,
                bpmnElement=self._SEQUENCE_FLOW_PREFIX + str(
                    mainflownodes + 1) + '_' + str(
                    subchaincount) + self._LAST_SUFFIX,
                sourceElement=self._SUBTASK_PREFIX + str(
                    mainflownodes) + '_' + str(
                    subchaincount) + '_' + str(len(chain)),
                targetElement=head + str(stepcount),
                nsmap=self._ns.NSMAP)
            BPMNLabel = etree.SubElement(BPMNEdge,
                                         self._ns.bpmndi + self._LABEL_SUFFIX,
                                         nsmap=self._ns.NSMAP)
            if subchaincount == 1:
                self._create_waypoint(BPMNEdge, currstart, self._Y_START)
                self._create_waypoint(BPMNEdge, xend, self._Y_START)
                etree.SubElement(
                    BPMNLabel, self._ns.dc + self._BOUNDS_SUFFIX,
                    x=str(xmid),
                    y=str(self._Y_LABEL),
                    width=str(self._WIDTH_LABEL),
                    height=str(self._HEIGHT_LABEL),
                    nsmap=self._ns.NSMAP)
            else:
                self._create_waypoint(
                    BPMNEdge, currstart, self._Y_START + ymove)
                self._create_waypoint(
                    BPMNEdge, xmid, self._Y_START + ymove)
                self._create_waypoint(BPMNEdge, xmid, self._Y_START)
                self._create_waypoint(BPMNEdge, xend, self._Y_START)
                etree.SubElement(
                    BPMNLabel, self._ns.dc + self._BOUNDS_SUFFIX,
                    x=str(xmid),
                    y=str(self._Y_START + ymove - self._OFFSET_Y_LABEL),
                    width=str(self._WIDTH_LABEL),
                    height=str(self._HEIGHT_LABEL),
                    nsmap=self._ns.NSMAP)
            ymove += gap + chainHeights[subchaincount - 1]
        BPMNShape = etree.SubElement(
            BPMNPlane, self._ns.bpmndi + self._SHAPE_SUFFIX,
            id=head + str(stepcount) + self._DI_SUFFIX,
            bpmnElement=head + str(stepcount),
            nsmap=self._ns.NSMAP)
        etree.SubElement(
            BPMNShape, self._ns.dc + self._BOUNDS_SUFFIX,
            x=str(xend),
            y=str(self._Y_START - self._OFFSET_BOUNDS),
            width=str(self._WIDTH_TASK),
            height=str(rounded_height),
            nsmap=self._ns.NSMAP)
        

    def _handlePlainNodeShapes(self, data, options, BPMNPlane, stepcount,
                               offset, planeHeight, xcurr, rounded_height):
        if len(options) == 0:
            BPMNShape = etree.SubElement(
                BPMNPlane, self._ns.bpmndi + self._SHAPE_SUFFIX,
                id=self._TASK_PREFIX + str(stepcount) + self._DI_SUFFIX,
                bpmnElement=self._TASK_PREFIX + str(stepcount),
                nsmap=self._ns.NSMAP)
            etree.SubElement(
                BPMNShape, self._ns.dc + self._BOUNDS_SUFFIX,
                x=str(xcurr + self._WIDTH_ARROW),
                y=str(self._Y_SHAPE_VARIANT),
                width=str(self._WIDTH_TASK),
                height=str(rounded_height),
                nsmap=self._ns.NSMAP)
            new_plane_height = rounded_height
            if planeHeight < new_plane_height:
                planeHeight = new_plane_height
            head = self._TASK_PREFIX
            BPMNEdge = etree.SubElement(
                BPMNPlane, self._ns.bpmndi + self._EDGE_SUFFIX,
                id=self._SEQUENCE_FLOW_PREFIX + str(
                    stepcount - 1) + self._DI_SUFFIX,
                bpmnElement=self._SEQUENCE_FLOW_PREFIX + str(stepcount - 1),
                sourceElement=head + str(stepcount - 1),
                targetElement=self._TASK_PREFIX + str(stepcount),
                nsmap=self._ns.NSMAP)
            self._create_waypoint(
                BPMNEdge, xcurr, self._Y_START)
            self._create_waypoint(
                BPMNEdge, xcurr + self._WIDTH_ARROW, self._Y_START)
            BPMNLabel = etree.SubElement(
                BPMNEdge, self._ns.bpmndi + self._LABEL_SUFFIX,
                nsmap=self._ns.NSMAP)
            etree.SubElement(
                BPMNLabel, self._ns.dc + self._BOUNDS_SUFFIX,
                x=str(round((xcurr + self._WIDTH_ARROW) / 2)),
                y=str(self._Y_LABEL),
                width=str(self._WIDTH_LABEL),
                height=str(self._HEIGHT_LABEL),
                nsmap=self._ns.NSMAP)
            maxchainlength = 0
            xcurr += self._WIDTH_ARROW + self._WIDTH_TASK

            # add timer icon main flow
            BPMNShape = etree.SubElement(
                BPMNPlane, self._ns.bpmndi + self._SHAPE_SUFFIX,
                id=f'{self._TASK_PREFIX}{stepcount}_Timer_{stepcount}',
                bpmnElement=self._TIMER_PREFIX + str(stepcount),
                nsmap=self._ns.NSMAP)
            etree.SubElement(
                BPMNShape, self._ns.dc + self._BOUNDS_SUFFIX,
                x=str(xcurr - 15),
                y=str(self._Y_LABEL_VARIANT + rounded_height + 10),
                width=str(32),
                height=str(32),
                nsmap=self._ns.NSMAP)
            BPMNLabel = etree.SubElement(
                BPMNShape, self._ns.bpmndi + self._LABEL_SUFFIX,
                nsmap=self._ns.NSMAP)
            y = str(self._Y_LABEL_VARIANT + rounded_height + 32)
            etree.SubElement(BPMNLabel, self._ns.dc + self._BOUNDS_SUFFIX,
                             x=str(xcurr - self._TASK_WIDTH + 30),
                             y=y,
                             width=str(self._WIDTH_LABEL_VARIANT),
                             height=str(self._HEIGHT_LABEL_VARIANT),
                             nsmap=self._ns.NSMAP)

        else:
            chains, maxchainlength = self.group_options(options)
            branchHeight, chainHeights = self._addBranchNodeShapes(
                options, chains, BPMNPlane, stepcount, offset, xcurr)
            self._addMergeNodeShapes(options, chains, BPMNPlane, stepcount,
                                     offset, chainHeights,
                                     maxchainlength, xcurr, rounded_height)
            xcurr += (maxchainlength + 1) * self._WIDTH_TASK + \
                (maxchainlength + 3) * self._WIDTH_ARROW + self._WIDTH_RHOMBUS
            if planeHeight < branchHeight:
                planeHeight = branchHeight

            # Add timer icon main flow after branch
            BPMNShape = etree.SubElement(
                BPMNPlane, self._ns.bpmndi + self._SHAPE_SUFFIX,
                id=f'{self._TASK_PREFIX}{stepcount}_Timer_{stepcount}',
                bpmnElement=self._TIMER_PREFIX + str(stepcount),
                nsmap=self._ns.NSMAP)
            etree.SubElement(
                BPMNShape, self._ns.dc + self._BOUNDS_SUFFIX,
                x=str(xcurr - 15),
                y=str(self._Y_LABEL_VARIANT + rounded_height + 10),
                width=str(32),
                height=str(32),
                nsmap=self._ns.NSMAP)
            BPMNLabel = etree.SubElement(
                BPMNShape, self._ns.bpmndi + self._LABEL_SUFFIX,
                nsmap=self._ns.NSMAP)
            y = str(self._Y_LABEL_VARIANT + rounded_height + 32)
            etree.SubElement(BPMNLabel, self._ns.dc + self._BOUNDS_SUFFIX,
                             x=str(xcurr - self._TASK_WIDTH + 30),
                             y=y,
                             width=str(self._WIDTH_LABEL_VARIANT),
                             height=str(self._HEIGHT_LABEL_VARIANT),
                             nsmap=self._ns.NSMAP)

        return planeHeight, maxchainlength, xcurr

    def _appendShapesAndEdges(self, BPMNPlane, data):
        stepcount = 0
        planeHeight = 0
        totalchainlength = 0
        options = []
        allnodes = []
        xcurr = self._OFFSET_X_APPEND_SHAPES_AND_EDGES
        BPMNShape = etree.SubElement(
            BPMNPlane, self._ns.bpmndi + self._SHAPE_SUFFIX,
            id=self._START_EVENT_0 + self._DI_SUFFIX,
            bpmnElement=self._START_EVENT_0, nsmap=self._ns.NSMAP)
        etree.SubElement(
            BPMNShape, self._ns.dc + self._BOUNDS_SUFFIX,
            x=str(xcurr),
            y=str(self._Y_SHAPE_VARIANT),
            width=str(self._WIDTH_START_EVENT),
            height=str(self._WIDTH_START_EVENT),
            nsmap=self._ns.NSMAP)
        BPMNLabel = etree.SubElement(
            BPMNShape, self._ns.bpmndi + self._LABEL_SUFFIX,
            nsmap=self._ns.NSMAP)
        etree.SubElement(
            BPMNLabel, self._ns.dc + self._BOUNDS_SUFFIX,
            x=str(xcurr - self._OFFSET_X_LABEL),
            y=str(self._Y_SHAPE_VARIANT_2),
            width=str(self._WIDTH_LABEL),
            height=str(self._HEIGHT_LABEL),
            nsmap=self._ns.NSMAP)
        BPMNEdge = etree.SubElement(
            BPMNPlane, self._ns.bpmndi + self._EDGE_SUFFIX,
            id=self._SEQUENCE_FLOW_0 + self._DI_SUFFIX,
            bpmnElement=self._SEQUENCE_FLOW_0,
            sourceElement=self._START_EVENT_0,
            targetElement=self._TASK_1_NAME,
            nsmap=self._ns.NSMAP)
        self._create_waypoint(
            BPMNEdge, xcurr + self._WIDTH_START_EVENT, self._Y_START)
        self._create_waypoint(
            BPMNEdge, xcurr + self._WIDTH_START_EVENT + self._WIDTH_ARROW,
            self._Y_START)
        BPMNLabel = etree.SubElement(
            BPMNEdge, self._ns.bpmndi + self._LABEL_SUFFIX,
            nsmap=self._ns.NSMAP)
        etree.SubElement(
            BPMNLabel, self._ns.dc + self._BOUNDS_SUFFIX,
            x=str(stepcount * self._WIDTH_TASK),
            y=str(self._Y_LABEL),
            width=str(self._WIDTH_LABEL),
            height=str(self._HEIGHT_LABEL),
            nsmap=self._ns.NSMAP)
        xcurr += self._WIDTH_START_EVENT + self._WIDTH_ARROW
        rounded_heights = []
        timers = []
        for step_num, step in self._process_steps.items():
            stepcount += 1
            if step.get(self._PROCESS_STEP_TITLE) is not None:
                if self._PROCESS_STEPS_STR==self._PROCESS_STEPS_DIGITAL_STR:
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
                    BPMNShape = etree.SubElement(
                        BPMNPlane, self._ns.bpmndi + self._SHAPE_SUFFIX,
                        id=self._TASK_PREFIX + str(
                            stepcount) + self._DI_SUFFIX,
                        bpmnElement=self._TASK_PREFIX + str(stepcount),
                        nsmap=self._ns.NSMAP)
                    etree.SubElement(
                        BPMNShape, self._ns.dc + self._BOUNDS_SUFFIX,
                        x=str(xcurr),
                        y=str(self._Y_SHAPE_VARIANT),
                        width=str(self._WIDTH_TASK),
                        height=str(rounded_height),
                        nsmap=self._ns.NSMAP)
                    allnodes.append(self._TASK_PREFIX + str(stepcount))
                    xcurr += self._WIDTH_TASK

                    # add timer icon
                    id_ = f'{self._TASK_PREFIX}{stepcount}_Timer_{stepcount}'
                    BPMNShape = etree.SubElement(
                        BPMNPlane, self._ns.bpmndi + self._SHAPE_SUFFIX,
                        id=id_,
                        bpmnElement=self._TIMER_PREFIX + str(stepcount),
                        nsmap=self._ns.NSMAP)
                    etree.SubElement(
                        BPMNShape, self._ns.dc + self._BOUNDS_SUFFIX,
                        x=str(xcurr - 15),
                        y=str(self._Y_LABEL_VARIANT + rounded_height + 10),
                        width=str(32),
                        height=str(32),
                        nsmap=self._ns.NSMAP)
                    BPMNLabel = etree.SubElement(
                        BPMNShape, self._ns.bpmndi + self._LABEL_SUFFIX,
                        nsmap=self._ns.NSMAP)
                    y = str(
                        self._Y_LABEL_VARIANT + rounded_height + 32)
                    etree.SubElement(BPMNLabel,
                                     self._ns.dc + self._BOUNDS_SUFFIX,
                                     x=str(xcurr - self._TASK_WIDTH + 30),
                                     y=y,
                                     width=str(self._WIDTH_LABEL_VARIANT),
                                     height=str(self._HEIGHT_LABEL_VARIANT),
                                     nsmap=self._ns.NSMAP)

                else:
                    if step.get(self._PROCESS_STEP_CHILD) == \
                            self._PROCESS_STEP_CHILD_YES:
                        options.append(step)
                    else:
                        planeHeight, maxBranchLength, xcurr = \
                            self._handlePlainNodeShapes(
                                data, options, BPMNPlane, stepcount,
                                self._OFFSET_HANDLE_PLAIN_NODE_SHAPES,
                                planeHeight, xcurr, rounded_height)
                        options = []
                        totalchainlength += maxBranchLength
                        allnodes.append(self._TASK_PREFIX + str(stepcount))
        BPMNShape = etree.SubElement(
            BPMNPlane, self._ns.bpmndi + self._SHAPE_SUFFIX,
            id=self._END_EVENT_PREFIX + str(stepcount + 1) + self._DI_SUFFIX,
            bpmnElement=self._END_EVENT_PREFIX + str(stepcount + 1),
            nsmap=self._ns.NSMAP)
        etree.SubElement(
            BPMNShape, self._ns.dc + self._BOUNDS_SUFFIX,
            x=str(xcurr + self._WIDTH_ARROW),
            y=str(self._Y_SHAPE_VARIANT), width=str(self._WIDTH_START_EVENT),
            height=str(self._WIDTH_START_EVENT), nsmap=self._ns.NSMAP)
        BPMNLabel = etree.SubElement(
            BPMNShape, self._ns.bpmndi + self._LABEL_SUFFIX,
            nsmap=self._ns.NSMAP)
        etree.SubElement(
            BPMNLabel, self._ns.dc + self._BOUNDS_SUFFIX,
            x=str(round(xcurr + self._WIDTH_ARROW / 2)),
            y=str(self._Y_SHAPE_VARIANT_2),
            width=str(self._WIDTH_LABEL),
            height=str(self._HEIGHT_LABEL),
            nsmap=self._ns.NSMAP)
        BPMNEdge = etree.SubElement(
            BPMNPlane, self._ns.bpmndi + self._EDGE_SUFFIX,
            id=self._SEQUENCE_FLOW_PREFIX + str(stepcount) + self._DI_SUFFIX,
            bpmnElement=self._SEQUENCE_FLOW_PREFIX + str(stepcount),
            sourceElement=self._TASK_PREFIX + str(stepcount),
            targetElement=self._END_EVENT_PREFIX + str(stepcount + 1),
            nsmap=self._ns.NSMAP)
        self._create_waypoint(
            BPMNEdge, xcurr, self._Y_START)
        self._create_waypoint(
            BPMNEdge, xcurr + self._WIDTH_ARROW, self._Y_START)
        BPMNLabel = etree.SubElement(
            BPMNEdge, self._ns.bpmndi + self._LABEL_SUFFIX,
            nsmap=self._ns.NSMAP)
        etree.SubElement(
            BPMNLabel, self._ns.dc + self._BOUNDS_SUFFIX,
            x=str(round(xcurr + self._WIDTH_ARROW / 2)),
            y=str(self._Y_LABEL),
            width=str(self._WIDTH_LABEL),
            height=str(self._HEIGHT_LABEL),
            nsmap=self._ns.NSMAP)
        return planeHeight + self._OFFSET_X_APPEND_SHAPES_AND_EDGES, xcurr

    def _appendDataObjectShapes(self, BPMNPlane, process_name, planeHeight,
                                boundsWidth):
        # Now add the shapes for the Evidences
        stepcount = 0
        maxtextheight = 0
        xcurr = self._OFFSET_X_DOC
        doc_y = planeHeight + self._OFFSET_Y_DOC
        evidenceRowsStarts = [doc_y]
        maxEvidencesPerRow = int(int(boundsWidth) / self._OFFSET_DOC_TAB)
        for evidence_num, evidence in self._process_evidences.items():
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
                BPMNShape = etree.SubElement(
                    BPMNPlane, self._ns.bpmndi + self._SHAPE_SUFFIX,
                    id=self._DATA_OBJECT_REFERENCE_PREFIX + str(
                        stepcount) + self._DI_SUFFIX,
                    bpmnElement=self._DATA_OBJECT_REFERENCE_PREFIX + str(
                        stepcount),
                    nsmap=self._ns.NSMAP)
                etree.SubElement(
                    BPMNShape, self._ns.dc + self._BOUNDS_SUFFIX,
                    x=str(xcurr + self._OFFSET_DOC_TAB),
                    y=str(evidenceRowsStarts[-1]),
                    width=str(self._WIDTH_DOC_ICON),
                    height=str(self._HEIGHT_DOC_ICON), nsmap=self._ns.NSMAP)
                BPMNLabel = etree.SubElement(
                    BPMNShape, self._ns.bpmndi + self._LABEL_SUFFIX,
                    nsmap=self._ns.NSMAP)
                y = str(
                    evidenceRowsStarts[-1] + self._OFFSET_EVIDENCES_Y_LABEL)
                etree.SubElement(
                    BPMNLabel, self._ns.dc + self._BOUNDS_SUFFIX,
                    x=str(round(xcurr + self._OFFSET_DOC_TAB / 2)),
                    y=y,
                    width=str(self._WIDTH_LABEL_VARIANT_2),
                    height=str(self._HEIGHT_LABEL),
                    nsmap=self._ns.NSMAP)
                xcurr += self._OFFSET_DOC_TAB
            # row is full no so continue to next row
            if stepcount % maxEvidencesPerRow == 0:
                evidence_rows_start = evidenceRowsStarts[-1] + \
                    maxtextheight + 2 * self._HEIGHT_DOC_ICON + \
                    self._OFFSET_X_DOC
                evidenceRowsStarts.append(evidence_rows_start)
                maxtextheight = 0
                xcurr = self._OFFSET_X_DOC
        return xcurr, evidenceRowsStarts[-1] + maxtextheight

    def _appendFlow(self, definition, process_name, data):
        # Add the generic shapes (the flow etc.)
        BPMNDiagram = etree.SubElement(
            definition, self._ns.bpmndi + self._DIAGRAM_SUFFIX,
            id=self._TRISOTECH_ID_6,
            nsmap=self._ns.NSMAP)
        BPMNDiagram.attrib[QName(self._ns.di_NAMESPACE, self._NAME_KEY)
                           ] = self._NAME_ATTR_PREFIX + process_name
        BPMNDiagram.attrib[QName(
            self._ns.di_NAMESPACE,
            self._DOCUMENTATION_KEY)] = self._DOCUMENTATION_ATTR
        BPMNDiagram.attrib[QName(self._ns.di_NAMESPACE, self._RESOLUTION_KEY)
                           ] = self._RESOLUTION_ATTR
        BPMNDiagram.attrib[QName(
            self._ns.xsi_NAMESPACE, self._TYPE_KEY)] = self._TYPE_ATTR
        BPMNPlane = etree.SubElement(
            BPMNDiagram, self._ns.bpmndi + self._PLANE_SUFFIX,
            bpmnElement=self._C_PREFIX + str(hash(process_name)),
            nsmap=self._ns.NSMAP)
        BPMNShape = etree.SubElement(
            BPMNPlane, self._ns.bpmndi + self._SHAPE_SUFFIX,
            id=self._TRISOTECH_ID + self._PARTICIPANT_PREFIX + str(
                hash(process_name)),
            bpmnElement=self._PARTICIPANT_PREFIX + str(hash(process_name)),
            isHorizontal=self._IS_HORIZONTAL_TRUE,
            nsmap=self._ns.NSMAP)
        # Now add the shapes for the main flow
        planeHeight, xcurr = self._appendShapesAndEdges(BPMNPlane, data)
        bounds_width = xcurr + self._WIDTH_START_EVENT + self._WIDTH_ARROW + \
            self._OFFSET_BOUNDS_WIDTH
        etree.SubElement(
            BPMNShape, self._ns.dc + self._BOUNDS_SUFFIX,
            x=str(self._X_SHAPE),
            y=str(self._Y_SHAPE_VARIANT_3),
            width=str(bounds_width),
            height=str(planeHeight),
            nsmap=self._ns.NSMAP)
        etree.SubElement(BPMNShape, self._ns.bpmndi + self._LABEL_SUFFIX,)
        return BPMNPlane, planeHeight, bounds_width

    def xml(self, data):
        root = etree.Element(self._DEFINITIONS_KEY)
        root.append(etree.Element(self._PROCESS_STR))
        semanticEl = etree.Element(
            f'{{{self._NAMESPACE[self._SEMANTIC_KEY]}}}{_SEMANTIC_STR}')
        etree.SubElement(
            semanticEl,
            f'{{{self._NAMESPACE[self._SEMANTIC_KEY]}}}{_DEFINITIONS_STR}')
        process_name = data.get(self._NAME_KEY)
        definition = etree.Element(
            self._ns.semantic + self._DEFINITIONS_KEY,
            id='_' + str(hash(process_name)),
            targetNamespace=self._NAMESPACE[self._XML_TARGET_KEY],
            nsmap=self._ns.NSMAP)
        # Read steps in order
        stringsorted = data.get(self._FIELDS_KEY).get(self._PROCESS_STEPS_STR)
        integerkeyed = {int(k): v for k, v in stringsorted.items()}
        self._process_steps = OrderedDict(
            sorted(integerkeyed.items(), key=lambda t: t[0]))
        # Read evidences in order
        ev_stringsorted = data.get(self._FIELDS_KEY).get(
            self._PROCESS_EVIDENCES_STR)
        ev_integerkeyed = {int(k): v for k, v in ev_stringsorted.items()}
        self._process_evidences = OrderedDict(
            sorted(ev_integerkeyed.items(), key=lambda t: t[0]))
        if self._process_steps is None:
            xml_string = ''
        else:
            process = self._appendProcessTree(definition, process_name, data)
            self._appendDataObjects(definition, process, data)
            self._appendCollaboration(definition, process_name)
            BPMNPlane, planeHeight, boundsWidth = self._appendFlow(
                definition, process_name, data)
            xdocmax, ydocmax = self._appendDataObjectShapes(
                BPMNPlane, process_name, planeHeight, boundsWidth)
            bs = BPMNPlane.findall(
                self._PLANE_FIND_ALL_QUERY, self._NAMESPACE)
            for b in bs:
                b.attrib[self._WIDTH_KEY] = str(
                    max(xdocmax, int(b.attrib[self._WIDTH_KEY])))
                b.attrib[self._HEIGHT_KEY] = str(ydocmax)
            dom = xml.dom.minidom.parseString(etree.tostring(
                definition, encoding='UTF-8', xml_declaration=True))
            xml_string = dom.toprettyxml()
        return xml_string