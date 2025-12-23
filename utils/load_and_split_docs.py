from services.RagdollService import RagdollService
import json

def load_and_split_docs(
        parent_id,
        document_type,
        load_fn, 
        load_params, 
        split_fn,
        extract_fn,
        meta=[],
        tags={}
    ):
    """
    Load and split documents using the provided functions and parameters.
    
    Args:
        parent_id (str | None): The source ID of the document to load's parent.
        document_type (str): The type of the document (e.g., GoogleDrive).
        load_fn (callable): Function to load documents.
        load_params (dict): Parameters for the loading function.
        split_fn (callable): Function to split documents.
        extract_fn (callable): Function to extract data from chunks.
    """
    
    # Load documents
    try:
        docs = load_fn(*load_params)
    except Exception as e:
        with (open("error.log", "a")) as f:
            f.write(f"Error loading documents: {e}\n")
        return

    print(docs)
    ragdoll = RagdollService()
    
    # Loop docs
    for i, doc in enumerate(docs):
        try:
            # Split doc into chunks
            chunks = split_fn([doc])
        except Exception as e:
            with (open(".temp/errors/doc_{i}.log", "a")) as f:
                f.write(f"Error splitting document: {e} {doc}\n")
            continue
        # Loop chunks
        for j, chunk in enumerate(chunks):
            # Set initial data
            data = {
                "parent_id": parent_id,
                "type": document_type,
                "index": j,
                "tags": tags,
            }
            try:
                # Update data with chunk information
                extracted_data = extract_fn(chunk, meta)
                data.update(extracted_data)
                # Send to ragdoll service
                # response = ragdoll.sendChunk(data)
                response = data
                with (open(f".temp/outputs/chunk_{extracted_data['meta']['video_id']}_{j}.log", "a")) as f:
                    f.write(f"Response from Ragdoll: {response}\n")
            except Exception as e:
                with (open(f".temp/errors/error_{i}_{j}.log", "a")) as f:
                    f.write(f"Error sending to Ragdoll: {e}\n")
                continue