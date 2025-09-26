1. Read dsl_reference.md in order to see how a .wf should be written.
2. Read the steps and create a file name tasks.txt that will tell the represent the block to be used. Wait until the file to be created to go to the next step
3. Read the first block inside the tasks.txt file and first step(steps have specific info of tasks.txt task), read the md of the block at that moment ALWAYS even if you already had read it( `.instructions/blocks/<name-of-block>.md)` for syntax and examples of the block at that instance, you NEED to do this in order to avoid errors, and keep adding to the workflow file(.wf) one block at a time. Create a workflow file with this block
4. Without asking me read the next block inside tasks.txt and next step and do step 3 again.. If there's no more blocks in the list stop.
5. Run `jelou workspace:deploy --dry-run` to validate\n\n**CRITICAL**: NEVER modify dsl_reference.md
