from django.shortcuts import render, redirect, get_object_or_404
from .models import WatchListItem
from inventory.models import Part 
from .forms import WatchListItemForm

def watchlist_list(request):
    items = WatchListItem.objects.all()
    context = {'items': items}
    return render(request, 'watchlist/watchlist_list.html', context)

def watchlist_detail(request, pk):
    item = get_object_or_404(WatchListItem, pk=pk)
    relevant_parts = Part.objects.filter(pen_model=item.pen_model)
    context = {
        'item': item,
        'relevant_parts': relevant_parts
    }
    return render(request, 'watchlist/watchlist_detail.html', context)

def add_watchlist_item(request):
    if request.method == 'POST':
        form = WatchListItemForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('watchlist-list')
    else:
        form = WatchListItemForm()
    context = {'form': form}
    return render(request, 'watchlist/watchlist_form.html', context)

def delete_watchlist_item(request, pk):
    item_to_delete = get_object_or_404(WatchListItem, pk=pk)
    if request.method == 'POST':
        item_to_delete.delete()
        return redirect('watchlist-list')
    return redirect('watchlist-list')