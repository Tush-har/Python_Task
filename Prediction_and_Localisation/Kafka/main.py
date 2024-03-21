from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from aiokafka import AIOKafkaConsumer
import asyncio
import json
from utils import CacheHelper
from PIL import Image, ImageDraw ,ImageFont
import base64
import io
# from utils import color_classes
from datetime import datetime
from bson.objectid import ObjectId
from collections import Counter

from utils import MongoHelper
app = FastAPI()

# This will keep track of connected WebSocket clients
connected_clients = set()


def draw_bounding_boxes(main_res, base64_image, color_classes):
    # Decode the base64 image
    image_data = base64.b64decode(base64_image)
    image = Image.open(io.BytesIO(image_data))
    # Create a drawing context
    draw = ImageDraw.Draw(image)
    # Choose a font (optional, default if not found)
    try:
        font = ImageFont.truetype("arial.ttf", 15)
    except IOError:
        font = ImageFont.load_default()
    # Create a reverse mapping from class name to color
    class_to_color = {cls: color for color, classes in color_classes.items() for cls in classes}
    # Iterate over the objects and draw their bounding boxes and labels
    for obj in main_res:
        box = obj['box']
        class_name = obj['name']
        confidence = obj['confidence']
        # Set the color based on the class name, default to green if not specified
        color = class_to_color.get(class_name, "green")
        draw.rectangle([box['x1'], box['y1'], box['x2'], box['y2']], outline=color, width=2)
        label = f"{class_name}: {confidence:.2f}"
        text_position = (box['x1'], box['y1'] - 15)
        draw.text(text_position, label, fill=color, font=font)

    # Convert the image back to base64
    image1 = image.copy()
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode() , image1

def count_checker(predcls_list,pv_valacc ,pv_valrjj,rej_checker):
    tmp = 0
    rej = False         # wiill help in mongo insertion
    for msg_val in predcls_list:
        if msg_val in rej_checker:
            tmp=1
    
    if tmp!=1:
        pv_valacc+=1

    else:
        pv_valacc+=tmp
        rej =True
    
    return pv_valacc, pv_valrjj , rej

global pv_val
pv_valacc = pv_valrjj = 0

async def consume():
    consumer = AIOKafkaConsumer(
        'camera_700006449005',
        bootstrap_servers='localhost:1093',
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    )
    await consumer.start()

    mongo_helper = MongoHelper()
    # db = mongo_helper.getDatabase()

    
    try:
        while True:
            rch = CacheHelper()
            # Check Redis key value for 'producer_trigger'
            should_consume = rch.get_json('producer_trigger')  # Removed 'await' here
            if should_consume: # Assuming the value is a string 'true' or 'false'
                try:
                    msg = await asyncio.wait_for(consumer.getone(), timeout=1.0)
                    # print(msg)
                    from utils import color_classes
                    result_base64 ,drawin_img = draw_bounding_boxes(msg.value['main_res'], msg.value['captured_image'], color_classes)
                    
                    rej_checker = color_classes.get('red')
                    pv_valacc ,pv_valrjj , rej= count_checker(msg.value['prediction classes'],pv_valacc ,pv_valrjj,rej_checker)
                    
                    ct_dict = Counter(msg.value['prediction classes'])
                    message = {'camera_serial':msg.value['camera_serial'],
                                     'captured_image':result_base64,
                                     'accepted':pv_valacc,
                                     'rejected':pv_valrjj
                                    
                                     }
                    
                                        # Convert the NumPy array to an image and save
                    
                    today =datetime.now().strftime("%d-%m-%Y")
                    current_time = datetime.now()
                    # Format the time to display only hours, minutes, and seconds
                    formatted_time = current_time.strftime("%H:%M:%S")

                    running_part_collection = mongo_helper.getCollection('running_part')

                    # Fetch the running part name
                    part_name = running_part_collection.find_one({}, {'part_name': 1})

                    pt_name = part_name['part_name']


                    if rej:
                        img_id = ObjectId()  # Generate a unique object ID for image naming
                        img_path = f"rejected_images/{img_id}.jpg"
                        Image.fromarray(drawin_img).save(img_path)
                        collection_name = f"{today}_ng" 
                        message_db = {
                            "img_path": img_path,
                            "defects": {
                                ct_dict
                            },
                            "part_name": pt_name,
                            'time': formatted_time
                        }
                    else:
                        collection_name = f"{today}_g" 
                        message_db = {
                            "img_path": img_path,
                            "accepts": {
                                ct_dict
                            },
                            "part_name": pt_name,
                            'time': formatted_time
                        }

                    collection = mongo_helper.getCollection(collection_name)
                    collection.insert_one(message_db)



                    for client in connected_clients:
                        await client.send_json(message)
                    # print(msg.value['main_res'])
                    # main_res = msg.value['main_res']
                    
                except asyncio.TimeoutError:
                    # No message in the last 1 second
                    continue
            else:
                # If the trigger is false, wait a bit before checking again
                print('here')
                await asyncio.sleep(1)  # You can adjust the sleep duration as needed
    finally:
        await consumer.stop()


@app.on_event("startup")
async def startup_event():
    # Start the Kafka consumer on startup
    asyncio.create_task(consume())

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.add(websocket)
    try:
        while True:
            # Just keep the connection open, we handle sending data in the consumer
            await websocket.receive_text()
    except WebSocketDisconnect:
        connected_clients.remove(websocket)




# Start the FastAPI application
# Use a command like `uvicorn main:app --host 0.0.0.0 --port 8200` to run the server
