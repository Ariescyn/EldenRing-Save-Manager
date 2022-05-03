Don't know the preffered way of listing planned updates, but this is what i would like to add in the future.

- In the stat editor, change validation of stat entry boxes to only allow the minimum level of any class.
    (or the class of the character once i figure out how to find it in the save file)
    For example, currently the minimum level you can enter is 5, but the lowest vigor you can have in the game is 9.
    
- Redo grid placements. I threw multiple items on the same row/column and just used padding to place them.

- Fix issue with GUI widgets changing sizes on different PC's. Listboxes or other widgets with bold font seem to change size.
    Currently i leave additional space on the right-side and bottom of the window to account for this, however that means content isn't centered.
    
- Performance improvements and simplification of hexedit.py. Functions like get_slot_ls and get_slot_slices unneccesarily open the file.
    A dictionary of hex addresses may be a simpler solution.
    - Replace confusing data concatenation like: slot_slices[char_num -1][0]  +  dest_char[:loc] by using fh.seek()
    - Reduce the scope of data that get_stats needs to iterate through

    
