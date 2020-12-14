import json
import requests
import xml.dom.minidom
from lxml import etree
from lxml.etree import QName


class BPMNNamespaces:
  def __init__(self, semantic, bpmndi, di, dc, xsi, NSMAP, di_NAMESPACE, xsi_NAMESPACE):
    self.semantic = semantic
    self.bpmndi = bpmndi
    self.di = di
    self.dc = dc
    self.xsi = xsi
    self.NSMAP = NSMAP
    self.di_NAMESPACE = di_NAMESPACE
    self.xsi_NAMESPACE = xsi_NAMESPACE

class BPMN:

  PROCESS_STEPS = None
  PROCESS_STEP_TITLE = None
  PROCESS_STEP_CHILD = None
  PROCESS_STEP_PREVIOUS_CHILD = None
  PROCESS_STEPS_DIGITAL = None
  taskWidth = 100
  arrowWidth = 50
  rhombusWidth = 50
  startEventWidth = 36

  NAMESPACE = {
      'semantic': 'http://www.omg.org/spec/BPMN/20100524/MODEL',
      'bpmndi': 'http://www.omg.org/spec/BPMN/20100524/DI',
      'di': 'http://www.omg.org/spec/DD/20100524/DI',
      'dc': 'http://www.omg.org/spec/DD/20100524/DC',
      'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
  }

  def __init__(self, digital_steps=False):
    self._init_constants(digital_steps=digital_steps)
    self._ns = BPMNNamespaces(
        semantic=f"{{{self.NAMESPACE['semantic']}}}",
        bpmndi=f"{{{self.NAMESPACE['bpmndi']}}}",
        di=f"{{{self.NAMESPACE['di']}}}",
        dc=f"{{{self.NAMESPACE['dc']}}}",
        xsi=f"{{{self.NAMESPACE['xsi']}}}",
        NSMAP=self.NAMESPACE,
        di_NAMESPACE=self.NAMESPACE['di'],
        xsi_NAMESPACE=self.NAMESPACE['xsi'])
    self._process_steps = None

  def group_options(self, opts):
    chains = {}
    for n in opts:
      # print(self.PROCESS_STEPS)
      if self.PROCESS_STEPS.endswith('digital'):
        curr = n.get('process_step_digital_num_id')
        prev = n.get('process_step_digital_previous_child')
      else:
        curr = n.get('process_step_num_id')
        prev = n.get('process_step_previous_child')
      # print(prev,'-',curr)
      # print(chains.get(prev))
      # print(len(chains),curr)
      if chains.get(prev) != None:
        arr = chains.get(prev)
        arr.append(n)
        chains.pop(prev, None)
        chains[curr] = arr
      else:
        arr = []
        arr.append(n)
        chains[curr] = arr
    # print(chains)
    maxchainlength = 0
    for k in chains:
      if len(chains.get(k)) > maxchainlength:
        maxchainlength = len(chains.get(k))
    return chains, maxchainlength

  def _create_waypoint(self, BPMNEdge, x, y):
    waypoint = etree.SubElement(
        BPMNEdge,
        self._ns.di + "waypoint",
        x=str(x),
        y=str(y),
        nsmap=self._ns.NSMAP)
    return waypoint

  def _init_constants(self, digital_steps=False):
    digital_str = 'digital'
    process_steps = 'Process steps'
    if digital_steps:
      process_steps += f' {digital_str}'
    digital_infix = f'_{digital_str}' if digital_steps else ''
    self.PROCESS_STEPS = process_steps
    self.PROCESS_STEP_TITLE = \
        f'process_step{digital_infix}_title'
    self.PROCESS_STEP_CHILD = f'process_step{digital_infix}_child'
    self.PROCESS_STEP_PREVIOUS_CHILD = f'process_step_previous{digital_infix}_child'

  def _appendStartEventTree(self, process, allnodes):
    ''''the method appends the xml elements of the StartEvent'''

    task = etree.SubElement(
        process, self._ns.semantic + "startEvent",
        id='StartEvent_0',
        name='Έναρξη', nsmap=self._ns.NSMAP)
    outgoing = etree.SubElement(
        task, self._ns.semantic + "outgoing",
        nsmap=self._ns.NSMAP)
    outgoing.text = 'SequenceFlow_0'
    allnodes.append('StartEvent_0')

  def _appendEndNodes(self, data, process, allnodes, options, stepcount):
    ''''the method appends the xml elements of the EndEvent'''
    stepname = "Λήξη"
    task = etree.SubElement(process, self._ns.semantic + "endEvent",
                            id='EndEvent_' + str(stepcount + 1),
                            name=stepname, nsmap=self._ns.NSMAP)
    incoming = etree.SubElement(
        task, self._ns.semantic + "incoming", nsmap=self._ns.NSMAP)
    incoming.text = 'SequenceFlow_' + str(stepcount)
    allnodes.append('EndEvent_' + str(stepcount + 1))
    # print(str(stepcount)+'================='+str(allnodes))
  # TBC
    task = etree.SubElement(
        process, self._ns.semantic + "sequenceFlow",
        id=('SequenceFlow_' + str(stepcount)),
        sourceRef=allnodes[stepcount],
        targetRef=allnodes[stepcount + 1],
        nsmap=self._ns.NSMAP)

  def _appendProcessTree(self, definition, process_name, data):
    process = etree.SubElement(definition, self._ns.semantic + "process",
                               id='pr_' + str(hash(process_name)),
                               isExecutable="false", nsmap=self._ns.NSMAP)
    laneSet = etree.SubElement(process, self._ns.semantic + "laneSet",
                               nsmap=self._ns.NSMAP)
    stepcount = 0
    allnodes = []
    options = []
    branched = False

    # add a default startEvent
    self._appendStartEventTree(process, allnodes)

    # parse the process steps and either add plainEventNodes, or put the branchNodes in a list and handle them when the first plainEventNode appears
    for step_num, step in self._process_steps.items():
      stepcount += 1
      if step.get(self.PROCESS_STEP_TITLE) is not None:
        stepname = step.get(self.PROCESS_STEP_TITLE)
        stepid = str(hash(stepname))
        # print('***',stepcount, step.get(self.PROCESS_STEP_CHILD))
        if step.get(self.PROCESS_STEP_CHILD) == 'Ναι':
          options.append(step)
          allnodes.append('Subtask_' + str(stepcount))
          branched = True
        else:
          # print(allnodes)
          self._handlePlainNodes(data, process, allnodes, options, stepcount)
          allnodes.append('Task_' + str(stepcount))
          # print(allnodes)
          options = []
        # TBC
          if branched != True:
            # print('***********************')
            # print(str(stepcount - 1),allnodes[stepcount-1],allnodes[stepcount])
            task = etree.SubElement(process,
                                    self._ns.semantic + "sequenceFlow",
                                    id='SequenceFlow_' + str(stepcount - 1),
                                    sourceRef=allnodes[stepcount - 1],
                                    targetRef=allnodes[stepcount],
                                    nsmap=self._ns.NSMAP)
          branched = False
    # add a default endEvent
    self._appendEndNodes(data, process, allnodes, options, stepcount)

  def _handlePlainNodes(self, data, process, allnodes, options, stepcount):

    # print('==>' + str(len(options)))
    process_steps = self._process_steps
    stepname = process_steps[stepcount - 1].get(
        self.PROCESS_STEP_TITLE)

    # if no BranchNodes are found
    if len(options) == 0:
      task = etree.SubElement(
          process, self._ns.semantic + "task",
          id='Task_' + str(stepcount),
          name=stepname, nsmap=self._ns.NSMAP)
      incoming = etree.SubElement(
          task, self._ns.semantic + "incoming", nsmap=self._ns.NSMAP)
      incoming.text = 'SequenceFlow_' + str(stepcount - 1)
      outgoing = etree.SubElement(
          task, self._ns.semantic + "outgoing", nsmap=self._ns.NSMAP)
      outgoing.text = 'SequenceFlow_' + str(stepcount)
    # if there are some BranchNodes from the previous event
    else:
      chains, maxchainlength = self.group_options(options)
      # print('===>' + str(len(chains)))

      self._addBranchNodes(options, chains, process, allnodes, stepcount)
      self._addMergeNodes(options, chains, process, allnodes,
                          stepcount, stepname, False)
      options = []

  def _appendCollaboration(self, definition, process_name):
    collaboration = etree.SubElement(
        definition,
        self._ns.semantic + "collaboration",
        id='C' + str(hash(process_name)),
        nsmap=self._ns.NSMAP)
    participant = etree.SubElement(
        collaboration, self._ns.semantic + "participant",
        id='participant_' + str(hash(process_name)),
        name=process_name,
        processRef='pr_' + str(hash(process_name)),
        nsmap=self._ns.NSMAP)

  def _addBranchNodes(self, options, chains, process, allnodes, stepcount):
    # add an exclusiveGateway node, with an incoming edge
    exclusiveGateway = etree.SubElement(
        process, self._ns.semantic + "exclusiveGateway",
        id='ExclusiveGateway_' + str(stepcount - len(options)),
        name='Επιλογή', nsmap=self._ns.NSMAP)

    incoming = etree.SubElement(
        exclusiveGateway,
        self._ns.semantic + "incoming",
        nsmap=self._ns.NSMAP)
    incoming.text = 'SequenceFlow_' + str(stepcount - len(options) - 1)

    # add a sequenceFlow for the exclusiveGateway's incoming edge
    # print(len(options), len(chains))
    task = etree.SubElement(
        process, self._ns.semantic + "sequenceFlow",
        id='SequenceFlow_' + str(stepcount - len(options) - 1),
        # gggggggggggggggggggg
        sourceRef=allnodes[stepcount - len(options) - 1],
        targetRef='ExclusiveGateway_' + str(stepcount - len(options)),
        nsmap=self._ns.NSMAP)

    # add now add i) the outgoing edges ii) the sequenceFlows for the outgoing edges,
    # iii) the subtasks, iv) their incoming and outgoing edges,
    # v) the respective SequenceFlows for these edges

    subchaincount = 0
    for key in chains:
      chain = chains.get(key)
      # print(key, chain)
      subchaincount += 1
      #  Handle the 1st node of each chain
      step = chain[0]
      # i)
      outgoing = etree.SubElement(
          exclusiveGateway,
          self._ns.semantic + "outgoing",
          nsmap=self._ns.NSMAP)
      # ii)  e.g. SequenceFlow_3_1_1, SequenceFlow_3_2_1  etc.
      outgoing.text = 'SequenceFlow_' + \
          str(stepcount - len(options)) + '_' + str(subchaincount) + '_1'
      # iii) e.g. Subtask_3_1_1, Subtask_3_2_1  etc.
      subTask = etree.SubElement(
          process, self._ns.semantic + "task",
          id='Subtask_' + str(
              stepcount - len(options)) + '_' + str(
              subchaincount) + '_1',
          name=step.get(self.PROCESS_STEP_TITLE),
          nsmap=self._ns.NSMAP)
      # set the current task as the last task of the chain
      lastTask = subTask
      # iv)
      incoming = etree.SubElement(
          subTask, self._ns.semantic + "incoming", nsmap=self._ns.NSMAP)
      incoming.text = 'SequenceFlow_' + \
          str(stepcount - len(options)) + '_' + \
          str(subchaincount) + '_' + str(1)
      task = etree.SubElement(process, self._ns.semantic + "sequenceFlow",
                              id='SequenceFlow_' + str(
                                  stepcount - len(options)) + '_' + str(
                                  subchaincount) + '_1',
                              sourceRef='ExclusiveGateway_' + str(
                                  stepcount - len(options)),
                              targetRef='Subtask_' + str(
                                  stepcount - len(options)) + '_' + str(
                                  subchaincount) + '_1', nsmap=self._ns.NSMAP)

      if (len(chain) > 1):
        self._add_chain_nodes(options, chain, process,
                              stepcount, subchaincount, lastTask)

      # in all cases
      outgoing = etree.SubElement(
          lastTask, self._ns.semantic + "outgoing", nsmap=self._ns.NSMAP)
      outgoing.text = 'SequenceFlow_' + \
          str(stepcount - len(options) + 1) + \
          '_' + str(subchaincount) + '_last'

  def _add_chain_nodes(self, options, chain, process, stepcount, subchaincount, lastTask):
    '''This method adds the reamaining nodes of a chain. If the case has more than one steps'''
    substepcount = 1
    for step in chain[1:]:
      substepcount += 1
      # print(node)
      curr_id = str(stepcount - len(options)) + '_' + \
          str(subchaincount) + '_' + str(substepcount)
      prev_id = str(stepcount - len(options)) + '_' + \
          str(subchaincount) + '_' + str(substepcount - 1)
      subTask = etree.SubElement(
          process, self._ns.semantic + "task",
          id='Subtask_' + curr_id,
          name=step.get(self.PROCESS_STEP_TITLE),
          nsmap=self._ns.NSMAP)
      outgoing = etree.SubElement(
          lastTask, self._ns.semantic + "outgoing", nsmap=self._ns.NSMAP)
      outgoing.text = 'SequenceFlow_' + curr_id
      incoming = etree.SubElement(
          subTask, self._ns.semantic + "incoming", nsmap=self._ns.NSMAP)
      incoming.text = 'SequenceFlow_' + curr_id
      etree.SubElement(process, self._ns.semantic + "sequenceFlow",
                       id='SequenceFlow_' + curr_id,
                       sourceRef='Subtask_' + prev_id,
                       targetRef='Subtask_' + curr_id, nsmap=self._ns.NSMAP)
      # set this task as the lastTask so that it can used in the next iteration as the previous node
      lastTask = subTask

  def _addMergeNodes(self, options, chains, process, allnodes, stepcount, stepname,
                     isEndNode):
    task = etree.SubElement(process, self._ns.semantic + "task",
                            id='Task_' + str(stepcount),
                            name=stepname, nsmap=self._ns.NSMAP)

    subchaincount = 0
    outgoing = etree.SubElement(
        task, self._ns.semantic + "outgoing", nsmap=self._ns.NSMAP)
    outgoing.text = 'SequenceFlow_' + str(stepcount)
    for k in chains:
      chain = chains.get(k)
      subchaincount += 1

      incoming = etree.SubElement(
          task, self._ns.semantic + "incoming", nsmap=self._ns.NSMAP)
      incoming.text = 'SequenceFlow_' + \
          str(stepcount - len(options) + 1) + \
          '_' + str(subchaincount) + '_last'

# append the SequenceFlows for the merge (but maybe it is better to move it to the merge)
      etree.SubElement(process, self._ns.semantic + "sequenceFlow",
                       id='SequenceFlow_' + str(
                           stepcount - len(options) + 1) + '_' + str(
                           subchaincount) + '_last',
                       sourceRef='Subtask_' + str(stepcount - len(options)) + '_' + str(
                           subchaincount) + '_' + str(len(chain)),
                       targetRef='Task_' + str(stepcount),
                       nsmap=self._ns.NSMAP)

  def _addBranchNodeShapes(self, options, chains, BPMNPlane, stepcount, offset,
                           boxHeightFactor, xcurr):
      # print(stepcount, len(options))
      # add the ExclusiveGateway shape
    mainflownodes = stepcount - len(options)
    BPMNShape = etree.SubElement(
        BPMNPlane, self._ns.bpmndi + "BPMNShape",
        id='ExclusiveGateway_' + str(mainflownodes) + '_di',
        bpmnElement='ExclusiveGateway_' + str(mainflownodes),
        isMarkerVisible="true", nsmap=self._ns.NSMAP)
    Bounds = etree.SubElement(
        BPMNShape, self._ns.dc + "Bounds",
        x=str(xcurr + self.arrowWidth),
        # x=str(mainflownodes * self.taskWidth),
        y=str(218), width=str(self.rhombusWidth), height=str(self.rhombusWidth),
        nsmap=self._ns.NSMAP)
    BPMNLabel = etree.SubElement(
        BPMNShape, self._ns.bpmndi + "BPMNLabel", nsmap=self._ns.NSMAP)
    Bounds = etree.SubElement(BPMNLabel, self._ns.dc + "Bounds",
                              x=str(xcurr + 15),
                              # x=str(15 + mainflownodes * self.taskWidth),
                              y=str(190), width=str(30), height=str(30),
                              nsmap=self._ns.NSMAP)

    # check if the previous flow node is the StartEvent or a simple Task
    head = 'Task_'
    # edgeoffset = self.taskWidth
    if stepcount == 2:
      head = 'StartEvent_'
      # edgeoffset = startEventWidth

    # draw an edge from the previous node to the ExclusiveGateway node
    BPMNEdge = etree.SubElement(
        BPMNPlane, self._ns.bpmndi + "BPMNEdge",
        id='SequenceFlow_' + str(mainflownodes - 1) + '_di',
        bpmnElement='SequenceFlow_' + str(mainflownodes - 1),
        sourceElement=head + str(stepcount - 1 - len(options)),
        targetElement='ExclusiveGateway_' + str(mainflownodes), nsmap=self._ns.NSMAP)
    waypoint = self._create_waypoint(
        BPMNEdge, xcurr, 240)
    # BPMNEdge, offset + edgeoffset + (mainflownodes - 1) * self.taskWidth, 240)
    waypoint = self._create_waypoint(
        BPMNEdge, xcurr + self.arrowWidth, 240)
    # BPMNEdge, offset - round(edgeoffset / 2) + mainflownodes * self.taskWidth, 240)
    BPMNLabel = etree.SubElement(
        BPMNEdge, self._ns.bpmndi + "BPMNLabel", nsmap=self._ns.NSMAP)
    # BPMNEdge, self._ns.bpmndi + "BPMNLabel", nsmap=self._ns.NSMAP)
    Bounds = etree.SubElement(
        BPMNLabel, self._ns.dc + "Bounds",
        # x=str(mainflownodes * self.taskWidth),
        x=str(round((xcurr + self.arrowWidth) / 2)),
        y=str(230), width=str(90),
        height=str(20), nsmap=self._ns.NSMAP)

    subchaincount = 0
    ymove = 0
    gap = 20
    xstart = xcurr + self.arrowWidth + self.rhombusWidth
    # xstart = offset + edgeoffset + (mainflownodes - 1) * self.taskWidth + 100
    ystart = 240
    xend = xstart + self.arrowWidth
    # xmax = xend
    maxChainLength = 1
    for k in chains:
      steps = chains.get(k)
      step = steps[0]
    # for step in options:
      subchaincount += 1
      BPMNShape = etree.SubElement(
          BPMNPlane, self._ns.bpmndi + "BPMNShape",
          id='Subtask_' + str(mainflownodes) + '_' +
          str(subchaincount) + '_1_di',
          bpmnElement='Subtask_' +
          str(mainflownodes) + '_' + str(subchaincount) + '_1',
          nsmap=self._ns.NSMAP)
      Bounds = etree.SubElement(
          BPMNShape, self._ns.dc + "Bounds",
          x=str(xend),
          y=str(218 + ymove),
          width=str(self.taskWidth),
          height=str(round(120 * boxHeightFactor)),
          nsmap=self._ns.NSMAP)
      if subchaincount == 1:
        BPMNEdge = etree.SubElement(
            BPMNPlane, self._ns.bpmndi + "BPMNEdge",
            id='SequenceFlow_' + str(mainflownodes) +
            '_' + str(subchaincount) + '_1_di',
            bpmnElement='SequenceFlow_' +
            str(mainflownodes) + '_' + str(subchaincount) + '_1',
            sourceElement='ExclusiveGateway_' + str(mainflownodes),
            targetElement='Subtask_' +
            str(mainflownodes) + '_' + str(subchaincount) + '_1',
            nsmap=self._ns.NSMAP)
        waypoint = self._create_waypoint(BPMNEdge, xstart, ystart)
        waypoint = self._create_waypoint(BPMNEdge, xend, ystart)
        BPMNLabel = etree.SubElement(BPMNEdge,
                                     self._ns.bpmndi + "BPMNLabel", nsmap=self._ns.NSMAP)
        Bounds = etree.SubElement(BPMNLabel, self._ns.dc + "Bounds",
                                  x=str(round(xend + xstart / 2)),
                                  y=str(230), width=str(90),
                                  height=str(20), nsmap=self._ns.NSMAP)
      else:
        BPMNEdge = etree.SubElement(
            BPMNPlane, self._ns.bpmndi + "BPMNEdge",
            id='SequenceFlow_' + str(mainflownodes) +
            '_' + str(subchaincount) + '_1_di',
            bpmnElement='SequenceFlow_' +
            str(mainflownodes) + '_' + str(subchaincount) + '_1',
            sourceElement='ExclusiveGateway_' + str(mainflownodes),
            targetElement='Subtask_' +
            str(mainflownodes) + '_' + str(subchaincount) + '_1',
            nsmap=self._ns.NSMAP)
        waypoint = self._create_waypoint(BPMNEdge, xstart, ystart)
        waypoint = self._create_waypoint(BPMNEdge, xstart, ystart + ymove)
        waypoint = self._create_waypoint(BPMNEdge, xend, ystart + ymove)
        BPMNLabel = etree.SubElement(
            BPMNEdge, self._ns.bpmndi + "BPMNLabel",
            nsmap=self._ns.NSMAP)
        Bounds = etree.SubElement(
            BPMNLabel, self._ns.dc + "Bounds",
            x=str(round(xend + xstart / 2)), y=str(230 + ymove),
            width=str(90), height=str(20),
            nsmap=self._ns.NSMAP)

      if len(steps) > 1:
        if len(steps) > maxChainLength:
          maxChainLength = len(steps)
        substepcount = 1
        for step in steps[1:]:
          # xfrom = xstart + self.arrowWidth+substepcount*100
          # xto = xend + self.arrowWidth+substepcount*100
          # if xto>xmax:
          #   xmax=xto
          substepcount += 1
          curr_subtask_id = str(mainflownodes) + '_' + \
              str(subchaincount) + '_' + str(substepcount)
          prev_subtask_id = str(mainflownodes) + '_' + \
              str(subchaincount) + '_' + str(substepcount - 1)
          BPMNShape = etree.SubElement(
              BPMNPlane, self._ns.bpmndi + "BPMNShape",
              id='Subtask_' + curr_subtask_id + '_di',
              bpmnElement='Subtask_' + curr_subtask_id,
              nsmap=self._ns.NSMAP)
          xnew = xstart + (self.arrowWidth + self.taskWidth) * \
              (substepcount - 1)
          Bounds = etree.SubElement(
              BPMNShape, self._ns.dc + "Bounds",
              x=str(xnew + self.arrowWidth),
              y=str(218 + ymove),
              width=str(self.taskWidth),
              height=str(round(120 * boxHeightFactor)),
              nsmap=self._ns.NSMAP)
          BPMNEdge = etree.SubElement(
              BPMNPlane, self._ns.bpmndi + "BPMNEdge",
              id='SequenceFlow_' + curr_subtask_id + '_di',
              bpmnElement='SequenceFlow_' + curr_subtask_id,
              sourceElement='Subtask_' + prev_subtask_id,
              targetElement='Subtask_' + curr_subtask_id,
              nsmap=self._ns.NSMAP)
          waypoint = self._create_waypoint(BPMNEdge, xnew, ystart + ymove)
          waypoint = self._create_waypoint(
              BPMNEdge, xnew + self.arrowWidth, ystart + ymove)
          BPMNLabel = etree.SubElement(BPMNEdge,
                                       self._ns.bpmndi + "BPMNLabel", nsmap=self._ns.NSMAP)
          Bounds = etree.SubElement(BPMNLabel, self._ns.dc + "Bounds",
                                    x=str(round(xnew + self.arrowWidth / 2)),
                                    y=str(230), width=str(90),
                                    height=str(20), nsmap=self._ns.NSMAP)

      ymove += gap + round(120 * boxHeightFactor)

    return ymove

  def _addMergeNodeShapes(self, options, chains, BPMNPlane, stepcount, offset,
                          boxHeightFactor, stepname, maxBranchLength, xcurr):
    head = 'Task_'
    xstart = xcurr + self.arrowWidth + \
        self.rhombusWidth + (self.arrowWidth + self.taskWidth)
    # edgeoffset = 100
    mainflownodes = stepcount - len(options)
    ymove = 0
    gap = 20
    # xstart = xend + edgeoffset
    # xstart = offset + edgeoffset + (mainflownodes-1) * self.taskWidth
    ystart = 240
    subchaincount = 0
    for k in chains:
      chain = chains.get(k)
      subchaincount += 1
      currstart = xstart + (len(chain) - 1) * \
          (self.arrowWidth + self.taskWidth)
      # currstart = xstart+(len(chain))*self.taskWidth
      # hhhhhhhhhhhhhhhhhhhhhhhhhhhh
      xend = xstart + (maxBranchLength - 1) * \
          (self.arrowWidth + self.taskWidth) + 2 * self.arrowWidth
      xmid = round((currstart + xend) / 2)
      BPMNEdge = etree.SubElement(
          BPMNPlane, self._ns.bpmndi + "BPMNEdge",
          id='SequenceFlow_' + str(mainflownodes + 1) +
          '_' + str(subchaincount) + '_last_di',
          bpmnElement='SequenceFlow_' +
          str(mainflownodes + 1) + '_' + str(subchaincount) + '_last',
          sourceElement='Subtask_' +
          str(mainflownodes) + '_' + str(subchaincount) + '_' + str(len(chain)),
          targetElement=head + str(stepcount),
          nsmap=self._ns.NSMAP)
      BPMNLabel = etree.SubElement(BPMNEdge, self._ns.bpmndi + "BPMNLabel",
                                   nsmap=self._ns.NSMAP)
      if subchaincount == 1:
        waypoint = self._create_waypoint(BPMNEdge, currstart, ystart)
        waypoint = self._create_waypoint(BPMNEdge, xend, ystart)
        Bounds = etree.SubElement(
            BPMNLabel, self._ns.dc + "Bounds",
            x=str(xmid), y=str(230), width=str(90), height=str(20),
            nsmap=self._ns.NSMAP)
      else:
        waypoint = self._create_waypoint(BPMNEdge, currstart, ystart + ymove)
        waypoint = self._create_waypoint(BPMNEdge, xmid, ystart + ymove)
        waypoint = self._create_waypoint(BPMNEdge, xmid, ystart)
        waypoint = self._create_waypoint(BPMNEdge, xend, ystart)
        Bounds = etree.SubElement(
            BPMNLabel, self._ns.dc + "Bounds",
            x=str(xmid), y=str(ystart + ymove - 10),
            width=str(90), height=str(20),
            nsmap=self._ns.NSMAP)

      ymove += gap + round(110 * boxHeightFactor)
    BPMNShape = etree.SubElement(
        BPMNPlane, self._ns.bpmndi + "BPMNShape",
        id=head + str(stepcount) + '_di',
        bpmnElement=head + str(stepcount),
        nsmap=self._ns.NSMAP)
    Bounds = etree.SubElement(
        BPMNShape, self._ns.dc + "Bounds",
        x=str(xend),
        y=str(ystart - 15),
        width=str(self.taskWidth),
        height=str(round(110 * boxHeightFactor)),
        nsmap=self._ns.NSMAP)
    # return xend

  def _handlePlainNodeShapes(self, data, options, BPMNPlane, stepcount,
                             offset, planeHeight, xcurr):
    # print('--->',xcurr)
    totalbranched = len(options)
    maxBranchLenght = 0
    stepname = self._process_steps[
        stepcount - 1].get(self.PROCESS_STEP_TITLE)
    boxHeightFactor = len(stepname) / 25
    if len(options) == 0:
        # print('Task_' + str(stepcount))
      BPMNShape = etree.SubElement(
          BPMNPlane, self._ns.bpmndi + "BPMNShape",
          id='Task_' + str(stepcount) + '_di',
          bpmnElement='Task_' + str(stepcount),
          nsmap=self._ns.NSMAP)
      Bounds = etree.SubElement(
          BPMNShape, self._ns.dc + "Bounds",
          x=str(xcurr + self.arrowWidth),
          # x=str(offset + stepcount * self.taskWidth),
          y=str(221),
          width=str(self.taskWidth),
          height=str(round(110 * boxHeightFactor)),
          nsmap=self._ns.NSMAP)
      if planeHeight < 110 * boxHeightFactor:
        planeHeight = 110 * boxHeightFactor
      prevstepname = self._process_steps[
          stepcount - 2].get(self.PROCESS_STEP_TITLE)
      prevstepid = str(hash(prevstepname))
      head = 'Task_'
      # edgeoffset = 100
      # if stepcount == 2:
      #     head = 'Task_'
      #     edgeoffset = 100
      BPMNEdge = etree.SubElement(
          BPMNPlane, self._ns.bpmndi + "BPMNEdge",
          id='SequenceFlow_' + str(stepcount - 1) + '_di',
          bpmnElement='SequenceFlow_' + str(stepcount - 1),
          sourceElement=head + str(stepcount - 1),
          targetElement='Task_' + str(stepcount),
          nsmap=self._ns.NSMAP)
      waypoint = self._create_waypoint(
          BPMNEdge, xcurr, 240)
      # BPMNEdge, offset + edgeoffset + (stepcount - 1) * self.taskWidth, 240)
      waypoint = self._create_waypoint(
          BPMNEdge, xcurr + self.arrowWidth, 240)
      # BPMNEdge, offset + stepcount * self.taskWidth, 240)
      BPMNLabel = etree.SubElement(
          BPMNEdge, self._ns.bpmndi + "BPMNLabel", nsmap=self._ns.NSMAP)
      Bounds = etree.SubElement(
          BPMNLabel, self._ns.dc + "Bounds",
          x=str(round((xcurr + self.arrowWidth) / 2)),
          y=str(230),
          width=str(90),
          height=str(20),
          nsmap=self._ns.NSMAP)
      maxchainlength = 0
      xcurr += self.arrowWidth + self.taskWidth
    else:
      chains, maxchainlength = self.group_options(options)
      branchHeight = self._addBranchNodeShapes(
          options, chains, BPMNPlane, stepcount, offset, boxHeightFactor, xcurr)
      self._addMergeNodeShapes(options, chains, BPMNPlane, stepcount,
                               offset, boxHeightFactor, stepname, maxchainlength, xcurr)
      xcurr += (maxchainlength + 1) * self.taskWidth + \
          (maxchainlength + 3) * self.arrowWidth + self.rhombusWidth
      if planeHeight < branchHeight:
        planeHeight = branchHeight
    return planeHeight, maxchainlength, xcurr

  def _appendShapesAndEdges(self, BPMNPlane, data):
    stepcount = 0
    offset = 50
    planeHeight = 0
    options = []
    allnodes = []
    totalchainlength = 0

    xcurr = 150

    BPMNShape = etree.SubElement(
        BPMNPlane, self._ns.bpmndi + "BPMNShape", id='StartEvent_0' + '_di',
        bpmnElement='StartEvent_0', nsmap=self._ns.NSMAP)
    Bounds = etree.SubElement(
        BPMNShape, self._ns.dc + "Bounds",
        x=str(xcurr), y=str(221),
        width=str(self.startEventWidth), height=str(self.startEventWidth), nsmap=self._ns.NSMAP)
    BPMNLabel = etree.SubElement(
        BPMNShape, self._ns.bpmndi + "BPMNLabel", nsmap=self._ns.NSMAP)
    Bounds = etree.SubElement(
        BPMNLabel, self._ns.dc + "Bounds",
        x=str(xcurr - 19), y=str(257), width=str(90), height=str(20),
        nsmap=self._ns.NSMAP)
    BPMNEdge = etree.SubElement(
        BPMNPlane, self._ns.bpmndi + "BPMNEdge",
        id='SequenceFlow_0' + '_di',
        bpmnElement='SequenceFlow_0',
        sourceElement='StartEvent_0',
        targetElement='Task_1',
        nsmap=self._ns.NSMAP)
    waypoint = self._create_waypoint(
        BPMNEdge, xcurr + self.startEventWidth, 240)
    # BPMNEdge, offset + 100 + edgeoffset + (stepcount) * self.taskWidth, 240)
    waypoint = self._create_waypoint(
        BPMNEdge, xcurr + self.startEventWidth + self.arrowWidth, 240)
    # BPMNEdge, offset + (stepcount+1) * self.taskWidth, 240)
    BPMNLabel = etree.SubElement(
        BPMNEdge, self._ns.bpmndi + "BPMNLabel", nsmap=self._ns.NSMAP)
    Bounds = etree.SubElement(
        BPMNLabel, self._ns.dc + "Bounds",
        x=str(stepcount * self.taskWidth),
        y=str(230),
        width=str(90),
        height=str(20),
        nsmap=self._ns.NSMAP)

    xcurr += self.startEventWidth + self.arrowWidth

    for step_num, step in self._process_steps.items():
      stepcount += 1
      if step.get(self.PROCESS_STEP_TITLE) is not None:
        stepname = step.get(self.PROCESS_STEP_TITLE)
        boxHeightFactor = len(stepname) / 25
        stepid = str(hash(stepname))
        if stepcount == 1:
          BPMNShape = etree.SubElement(
              BPMNPlane, self._ns.bpmndi + "BPMNShape",
              id='Task_' + str(stepcount) + '_di',
              bpmnElement='Task_' + str(stepcount),
              nsmap=self._ns.NSMAP)
          Bounds = etree.SubElement(
              BPMNShape, self._ns.dc + "Bounds",
              x=str(xcurr),
              # x=str(offset + stepcount * self.taskWidth),
              y=str(221),
              width=str(self.taskWidth), height=str(round(100 * boxHeightFactor)),
              nsmap=self._ns.NSMAP)
          allnodes.append('Task_' + str(stepcount))
          xcurr += self.taskWidth
        else:
          if step.get(self.PROCESS_STEP_CHILD) == 'Ναι':
            options.append(step)
          else:
            # print('*1**',xcurr)
            planeHeight, maxBranchLength, xcurr = self._handlePlainNodeShapes(
                data, options, BPMNPlane, stepcount, offset,
                planeHeight, xcurr)
            # print('*2**',xcurr)
            options = []
            totalchainlength += maxBranchLength
            allnodes.append('Task_' + str(stepcount))
    # gggggggggggggggg
    # edgeoffset = 100
    BPMNShape = etree.SubElement(
        BPMNPlane, self._ns.bpmndi + "BPMNShape",
        id='EndEvent_' + str(stepcount + 1) + '_di',
        bpmnElement='EndEvent_' + str(stepcount + 1),
        nsmap=self._ns.NSMAP)
    Bounds = etree.SubElement(
        BPMNShape, self._ns.dc + "Bounds",
        x=str(xcurr + self.arrowWidth),
        # x=str(150+(stepcount-len(options)+totalchainlength)*self.taskWidth+edgeoffset),
        y=str(221), width=str(self.startEventWidth),
        height=str(self.startEventWidth), nsmap=self._ns.NSMAP)
    BPMNLabel = etree.SubElement(
        BPMNShape, self._ns.bpmndi + "BPMNLabel",
        nsmap=self._ns.NSMAP)
    Bounds = etree.SubElement(
        BPMNLabel, self._ns.dc + "Bounds",
        x=str(round(xcurr + self.arrowWidth / 2)),
        # x=str(131+(stepcount-len(options)+totalchainlength)*self.taskWidth+edgeoffset),
        y=str(257),
        width=str(90),
        height=str(20),
        nsmap=self._ns.NSMAP)
    # edgeoffset=36
    BPMNEdge = etree.SubElement(
        BPMNPlane, self._ns.bpmndi + "BPMNEdge",
        id='SequenceFlow_' + str(stepcount) + '_di',
        bpmnElement='SequenceFlow_' + str(stepcount),
        sourceElement='Task_' + str(stepcount),
        targetElement='EndEvent_' + str(stepcount + 1),
        nsmap=self._ns.NSMAP)
    waypoint = self._create_waypoint(
        BPMNEdge, xcurr, 240)
    # BPMNEdge, edgeoffset + (stepcount-len(options)+totalchainlength) * self.taskWidth, 240)
    waypoint = self._create_waypoint(
        BPMNEdge, xcurr + self.arrowWidth, 240)
    # BPMNEdge, offset + (stepcount-len(options)+totalchainlength+1) * self.taskWidth, 240)
    BPMNLabel = etree.SubElement(
        BPMNEdge, self._ns.bpmndi + "BPMNLabel", nsmap=self._ns.NSMAP)
    Bounds = etree.SubElement(
        BPMNLabel, self._ns.dc + "Bounds",
        # x=str((stepcount-1) * self.taskWidth),
        x=str(round(xcurr + self.arrowWidth / 2)),
        y=str(230),
        width=str(90),
        height=str(20),
        nsmap=self._ns.NSMAP)

    return planeHeight + 150, xcurr

  def _appendFlow(self, definition, process_name, data):
    # add the generic shapes (the flow etc.)
    planeWidthRatio = 220
    BPMNDiagram = etree.SubElement(
        definition, self._ns.bpmndi + "BPMNDiagram",
        id='Trisotech.Visio-_6',
        nsmap=self._ns.NSMAP)
    BPMNDiagram.attrib[QName(self._ns.di_NAMESPACE, 'name')
                       ] = "Collaboration Diagram for " + process_name
    BPMNDiagram.attrib[QName(self._ns.di_NAMESPACE, 'documentation')] = ""
    BPMNDiagram.attrib[QName(self._ns.di_NAMESPACE, 'resolution')
                       ] = "96.00000267028808"
    BPMNDiagram.attrib[QName(self._ns.xsi_NAMESPACE, 'type')] = "dc:Point"

    BPMNPlane = etree.SubElement(
        BPMNDiagram, self._ns.bpmndi + "BPMNPlane",
        bpmnElement='C' + str(hash(process_name)),
        nsmap=self._ns.NSMAP)
    BPMNShape = etree.SubElement(
        BPMNPlane, self._ns.bpmndi + "BPMNShape",
        id='Trisotech.Visio_' + 'participant_' + str(
            hash(process_name)),
        bpmnElement='participant_' + str(hash(process_name)),
        isHorizontal='true',
        nsmap=self._ns.NSMAP)

    # Now add the shapes for the main flow
    planeHeight, xcurr = self._appendShapesAndEdges(BPMNPlane, data)

    Bounds = etree.SubElement(
        BPMNShape, self._ns.dc + "Bounds",
        x=str(100), y=str(111),
        width=str(xcurr + self.startEventWidth + self.arrowWidth + 50),
        # width=str(planeWidthRatio * len(self._process_steps) + 1),
        height=str(planeHeight),
        nsmap=self._ns.NSMAP)
    BPMNLabel = etree.SubElement(BPMNShape, self._ns.bpmndi + "BPMNLabel",)

  def xml(self, data, file=None):
    root = etree.Element("definitions")
    root.append(etree.Element("process"))
    semanticEl = etree.Element(f"{{{self.NAMESPACE['semantic']}}}semantic")
    definitions = etree.SubElement(
        semanticEl, f"{{{self.NAMESPACE['semantic']}}}definitions")
    process_name = data.get('name')
    definition = etree.Element(
        self._ns.semantic + "definitions",
        id='_' + str(hash(process_name)),
        targetNamespace='http://www.trisotech.com/definitions/_1276276944297',
        nsmap=self._ns.NSMAP)
    self._process_steps = data.get('fields').get(self.PROCESS_STEPS)

    if self._process_steps is None:
      xml_string = ''
    else:
      self._appendProcessTree(definition, process_name, data)
      self._appendCollaboration(definition, process_name)
      self._appendFlow(definition, process_name, data)
      dom = xml.dom.minidom.parseString(etree.tostring(
          definition, encoding='UTF-8', xml_declaration=True))
      xml_string = dom.toprettyxml()
      if file is not None:
        with open(file, "w+") as f:
          f.write(xml_string)
    return xml_string
