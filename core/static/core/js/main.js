$(document).ready(function () {
  // code here
  $('input,textarea,select').addClass('w-full border-2 border-gray-300 px-3 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-600 focus:border-transparent');
  $('textarea').attr('rows', '3');

  // ADD FORM
  // bpmn-diagram - adding the BPMN diagram to the ADD FORM
  const diagramContainer = document.getElementById('bpmn-diagram');
  if (diagramContainer) {
    const bpmnModeler = new BpmnJS({
      container: diagramContainer,
      keyboard: {
        bindTo: window
      }
    });
    let elementSelected = null
    const durationInput = document.getElementById('id_duration');
    const groupInput = document.getElementById('id_group_select');
    const percentInput = document.getElementById('id_percent');
    const inputDiv = document.getElementById('bpmn-inputs')
    const sequenceDiv = document.getElementById("bpmn-sequence")
    const conditionInp = document.getElementById("id_condition")
    const defaultInp = document.getElementById("id_default_select")
    const bpmnInp = document.getElementById('id_bpmn') // this is the bpmn input field



    let canvas = bpmnModeler.get('canvas');
    let overlays = bpmnModeler.get('overlays');
    let modeling = bpmnModeler.get('modeling')
    let eventBus = bpmnModeler.get('eventBus');
    let elementRegistry = bpmnModeler.get('elementRegistry')

    if (bpmnInp.value) {
      bpmnModeler.importXML(bpmnInp.value).then(function () { 
        console.log('import is done');
      })
    }
    else {
      bpmnModeler.createDiagram()
    }
    
    canvas.zoom('fit-viewport');

    // functions
    async function exportDiagram() {
      let result = null
      try {
        result = await bpmnModeler.saveXML({ format: true });
        // console.log('DIAGRAM', result.xml);
      } catch (err) {
        console.error('could not save BPMN 2.0 diagram', err);
      }

      return result
    }


    durationInput.addEventListener('change', (e) => {
      if (elementSelected) {
        value = e.target.value
        const element = elementRegistry.get(elementSelected)
        modeling.updateProperties(element, { duration: value })
        exportDiagram().then(exported => {
          bpmnInp.value = exported.xml
        })
      }
    })

    percentInput.addEventListener('change', (e) => {
      if (elementSelected) {
        value = e.target.value
        const element = elementRegistry.get(elementSelected)
        modeling.updateProperties(element, { percent: value })
        exportDiagram().then(exported => {
          bpmnInp.value = exported.xml
        })
      }
    })
    groupInput.addEventListener('change', (e) => {
      if (elementSelected) {
        value = e.target.value
        const element = elementRegistry.get(elementSelected)
        modeling.updateProperties(element, { group: value })
        exportDiagram().then(exported => {
          bpmnInp.value = exported.xml
        })
      }
    })

    conditionInp.addEventListener('change', (e) => {
      if (elementSelected) {
        value = e.target.value
        const element = elementRegistry.get(elementSelected)
        modeling.updateProperties(element, { condition: value })
        exportDiagram().then(exported => {
          bpmnInp.value = exported.xml
        })
      }
    })
    defaultInp.addEventListener('change', (e) => {
      if (elementSelected) {
        value = e.target.value
        const element = elementRegistry.get(elementSelected)
        modeling.updateProperties(element, { is_default: value })
        exportDiagram().then(exported => {
          bpmnInp.value = exported.xml
        })
      }
    })


    
    function showInputs() {
      if(inputDiv.classList.contains('hidden')){
        inputDiv.classList.remove('hidden')
      }
    }
    function hideInputs() {
      if(!inputDiv.classList.contains('hidden')){
        inputDiv.classList.add('hidden')
      }
    }
    function showSequenceFlowInputs() {
      if(sequenceDiv.classList.contains('hidden')){
        sequenceDiv.classList.remove('hidden')
      }
    }
    function hideSequenceFlowInputs() {
      if(!sequenceDiv.classList.contains('hidden')){
        sequenceDiv.classList.add('hidden')
      }
    }


    
    
    bpmnModeler.on('element.click', function (event) {
      console.log(event);
      console.log(event.element);
      if (event.element.type == 'bpmn:Task') {
        elementSelected = null
        durationInput.value = ""
        percentInput.value = ""
        groupInput.value = ""
        conditionInp.value = ""
        defaultInp.value = ""
        elementSelected = event.element.id
        showInputs()
        hideSequenceFlowInputs()
        const element = elementRegistry.get(elementSelected)
        if(element.businessObject.get('duration')) durationInput.value = element.businessObject.get('duration')
        if (element.businessObject.get('percent')) percentInput.value = element.businessObject.get('percent')
        if (element.businessObject.get('group')) groupInput.value = element.businessObject.get('group')
        
      } else if (event.element.type == 'bpmn:SequenceFlow') {
        elementSelected = null
        durationInput.value = ""
        percentInput.value = ""
        groupInput.value = ""
        conditionInp.value = ""
        defaultInp.value = ""

        elementSelected = event.element.id
        showSequenceFlowInputs()
        hideInputs()
        const element = elementRegistry.get(elementSelected)
        if(element.businessObject.get('condition')) conditionInp.value = element.businessObject.get('condition')
        if (element.businessObject.get('is_default')) defaultInp.value = element.businessObject.get('is_default')


      }
      
      else {
        elementSelected = null
        durationInput.value = ""
        percentInput.value = ""
        groupInput.value = ""
        conditionInp.value = ""
        defaultInp.value = ""

        hideInputs()
        hideSequenceFlowInputs()
      }
    })
    bpmnModeler.on('commandStack.shape.create.executed', function (event) {
      if (event.context.shape.type == 'bpmn:Task') {
        elementSelected = null
        durationInput.value = ""
        percentInput.value = ""
        groupInput.value = ""
        conditionInp.value = ""
        defaultInp.value = ""
        showInputs()
        elementSelected = event.context.shape.id


      }
      else {
        elementSelected = null
        hideInputs()
        durationInput.value = ""
        percentInput.value = ""
        groupInput.value = ""

      }
      canvas.zoom('fit-viewport');
      exportDiagram().then(exported => {
        bpmnInp.value = exported.xml
      })
    })
    bpmnModeler.on('commandStack.changed', function (event) {
      exportDiagram().then(exported => {
        bpmnInp.value = exported.xml
      })
    })


  }


  async function openDiagram(bpmnViewer,bpmnXML) {
    try {
      await bpmnViewer.importXML(bpmnXML);
      var canvas = bpmnViewer.get('canvas');
      canvas.zoom('fit-viewport');
    } catch (err) {

      console.error('could not import BPMN 2.0 diagram', err);
    }
  }

  const bpmnViews = document.querySelectorAll('.bpmn-view')
  if (bpmnViews) {
    bpmnViews.forEach(function (view) {
      let dones = view.getAttribute("data-done")
      if (dones) {
        dones = dones.replace("[", "").replace("]", "").split(",")
        dones = dones.map(done => {
          return done.trim().replaceAll("'", "")
        })
      }
      let showInputs = view.getAttribute("data-show-inputs")
      const parent = view.parentElement
      const diagram = new BpmnJS({
        container: parent,
        keyboard: {
          bindTo: window
        }
      });
      
      diagram.importXML(view.textContent).then(function () {
        var canvas = diagram.get('canvas');
        const overlays = diagram.get('overlays')
        const elementRegistry = diagram.get('elementRegistry')
        console.log(elementRegistry);
        canvas.zoom('fit-viewport');
        if (dones) {
          for (let done of dones) {
            if(done) canvas.addMarker(done, 'highlight-green');
            
          }
        }
        if (showInputs == "true") {
          console.log('object');
         }



      });

    })
  }



  const modalBtns = document.querySelectorAll('.modal-toggle')
  if (modalBtns) {
    modalBtns.forEach(function (btn) {
      btn.addEventListener('click', function (e) {

        const modal = document.querySelector(btn.getAttribute('data-modal'))
        modal.classList.toggle('hidden')

        // if data-acitivity id
        const acitivityId = btn.getAttribute('data-activity-id')
        if(acitivityId){
          const acitivityInp = document.querySelector("#activity_id_refer_form")
          acitivityInp.value=acitivityId
        }

        const referForm = document.querySelector("#refer_form")
        if (referForm) {
          referForm.setAttribute("action",btn.getAttribute("data-action-url"))
        }
        

      })
    })
  }
  const modals = document.querySelectorAll('.modal')
  if (modals) { 
    modals.forEach(function (modal) {
      modal.addEventListener('click', function (event) {
        const taget = event.target
        if (taget.classList.contains('modal')) {
          modal.classList.toggle('hidden')
        }
      })
      
    })
  }        

  // let events = [
  //   'commandStack.shape.create.executed',
  // ]
  // events.forEach(function(event){
  //   eventBus.on(event, function(e) {
  //     console.log(event, e);
  //     console.log(e.context.shape.id);
  //     ipn.value = e.context.shape.id
  //     // console.log(e.context.shape.businessObject);
  //     // moddling.updateProperties(e.context.shape,{
  //     //   max:10
  //     // })
  //   })
  // })

  let confirms = document.querySelectorAll('.confirm')
  for (let confirm of confirms) {
    confirm.addEventListener('click', function (event) {
      event.preventDefault()
      const bpmn = new BpmnJS({});

      const target = event.target
      const activityID = target.getAttribute('data-activity-id')
      const bpmnInp = document.querySelector("#id_bpmn_confirm"+"_"+activityID)
      const activityInp = document.getElementById("id_activity_id"+"_"+activityID)
      const doneActivities = target.getAttribute("data-tasks-done")

      bpmn.importXML(bpmnInp.value).then(function () { 

        const elementRegistry = bpmn.get('elementRegistry')
        const element = elementRegistry.get(activityInp.value)
        const outgoing = element.outgoing
        const flow = outgoing[0]
        const flowTarget = flow.target
        const nextFlow = document.getElementById("id_next_activity"+"_"+activityID)
        const groupInp = document.getElementById("id_group"+"_"+activityID)
        const durationInp = document.getElementById("id_duration"+"_"+activityID)
        const percentInp = document.getElementById("id_percent"+"_"+activityID)
        const nextFlowInp = document.getElementById("id_next_activity_type"+"_"+activityID)
        const activityName = document.getElementById("id_activity_name" + "_" + activityID)
        
        console.log(flowTarget);
        console.log(flowTarget.type);

        if (flowTarget.type == "bpmn:Task") {

          nextFlowInp.value = flowTarget.type
          groupInp.value = flowTarget.businessObject.get("group") || ""
          durationInp.value = flowTarget.businessObject.get("duration") || ""
          percentInp.value = flowTarget.businessObject.get("percent") || ""
          nextFlow.value = flowTarget.id
          activityName.value = flowTarget.businessObject.name
          target.closest("form").submit()
          // end of if for task nodes
        } else if (flowTarget.type == "bpmn:ExclusiveGateway") {
          const conditions = flowTarget.outgoing
          const modal = document.getElementById("activity-choose-path")
          modal.classList.remove("hidden")

          const selectInp = document.getElementById("id_path")
          for (let condition of conditions) {
            const option = document.createElement('option');
            option.value = condition.id;
            option.text = condition.businessObject.get("condition");
            if(condition.businessObject.get("is_default") == "1"){
              option.selected = true;
            }
            selectInp.add(option);
          }

          const pathBtn = document.getElementById("path-btn")
          pathBtn.addEventListener('click', function () {
            const path = selectInp.value
            const flow = elementRegistry.get(path)
            const targetRef = flow.businessObject.targetRef
            const targetElement = elementRegistry.get(targetRef.id)

            nextFlowInp.value = targetElement.type
            groupInp.value = targetElement.businessObject.get("group") || ""
            durationInp.value = targetElement.businessObject.get("duration") || ""
            percentInp.value = targetElement.businessObject.get("percent") || ""
            nextFlow.value = targetElement.id
            activityName.value = targetElement.businessObject.name
            target.closest("form").submit()
            
          })
          // end of if for exclusive gateway
        } else if (flowTarget.type == 'bpmn:EndEvent') {
          nextFlowInp.value = flowTarget.type
          groupInp.value = flowTarget.businessObject.get("group") || ""
          durationInp.value = flowTarget.businessObject.get("duration") || ""
          percentInp.value = flowTarget.businessObject.get("percent") || ""
          nextFlow.value = flowTarget.id
          activityName.value = flowTarget.businessObject.name
          target.closest("form").submit()
        
          // end of if for endEvent
        } else if (flowTarget.type == 'bpmn:ParallelGateway') {
          const outgoings = flowTarget.outgoing
          const incomings = flowTarget.incoming
          
          // starting the parallelGate
          if (outgoings.length > 1) {
            nextFlowInp.value = flowTarget.type
            for (const outgoing of outgoings) {
              const targetRefParallel = outgoing.businessObject.targetRef
              const parallelTask = elementRegistry.get(targetRefParallel.id)

              
              groupInp.value +=":::"+ parallelTask.businessObject.get("group") || ""
              durationInp.value +=":::"+ parallelTask.businessObject.get("duration") || ""
              percentInp.value +=":::"+ parallelTask.businessObject.get("percent") || ""
              nextFlow.value +=":::"+ parallelTask.id
              activityName.value +=":::"+ parallelTask.businessObject.name
            }
            target.closest("form").submit()
  
          }// ending the parallelGate
          else {
            let doneActivitiesArray = doneActivities.replaceAll("[", "").replaceAll("]", "").replaceAll("'", "").replaceAll(" ","").split(",")
            //
            // check if all the requirments are done
            const current_activity = element.id
            let related_activities = []
            for (flow_id of incomings) {
              related_activities.push(flow_id.businessObject.sourceRef.id);
            }

            related_activities = related_activities.filter(item => item !== current_activity);
            let count_done = 0
            for (item of related_activities) {
              if (doneActivitiesArray.indexOf(item) !== -1) {
                // Item exists in the array
                count_done += 1
              }
            }
            if (count_done == related_activities.length) {
              const elementAfterGate = elementRegistry.get(outgoings[0].businessObject.targetRef.id)
              nextFlowInp.value = elementAfterGate.type
              groupInp.value = elementAfterGate.businessObject.get("group") || ""
              durationInp.value = elementAfterGate.businessObject.get("duration") || ""
              percentInp.value = elementAfterGate.businessObject.get("percent") || ""
              nextFlow.value = elementAfterGate.id
              activityName.value = elementAfterGate.businessObject.name
    
            }






            target.closest("form").submit()
          }

          // end of if for parallelGateway
        }
        


        // end of importing xml
      })

      // end if add eventlistner
    })
  }
  // end of document ready
});
