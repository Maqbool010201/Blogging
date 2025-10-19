from django import template
from django.db.models import Q
from django.utils import timezone
import random
from blogs.models import Advertisement

register = template.Library()

@register.inclusion_tag('blogs/includes/advertisement.html')
def show_ad(placement_area, post_category_id=None, ad_size='auto', ad_type=None):
    """
    Enhanced ad tag with category targeting and smart ad selection
    """
    now = timezone.now()
    
    # Build proper filters with date range checking
    filters = Q(placement_area=placement_area, is_active=True)
    filters &= Q(start_date__lte=now) | Q(start_date__isnull=True)
    filters &= Q(end_date__gte=now) | Q(end_date__isnull=True)
    
    if ad_type:
        filters &= Q(ad_type=ad_type)
    
    # Get ads with placement priority
    available_ads = Advertisement.objects.filter(filters).order_by('-priority', '?')
    
    # Filter by category if provided
    if post_category_id and available_ads.exists():
        category_filtered_ads = []
        for ad in available_ads:
            # If ad has target categories, check if it matches the post category
            if ad.target_categories.exists():
                if ad.target_categories.filter(id=post_category_id).exists():
                    category_filtered_ads.append(ad)
            else:
                # If no target categories specified, include the ad
                category_filtered_ads.append(ad)
        
        if category_filtered_ads:
            available_ads = category_filtered_ads
    
    # Select ad based on display strategy
    selected_ad = None
    if available_ads:
        selected_ad = select_ad_by_strategy(available_ads)
        
        # Increment impression count if ad is selected
        if selected_ad:
            selected_ad.impressions += 1
            selected_ad.save(update_fields=['impressions'])
    
    return {
        'ad': selected_ad,
        'placement_area': placement_area,
        'ad_size': ad_size,
        'post_category_id': post_category_id,
    }

@register.simple_tag
def get_multiple_ads(placement_area, count=3, post_category_id=None, ad_type=None):
    """
    Get multiple ads for carousels or multiple placements with category targeting
    """
    now = timezone.now()
    
    filters = Q(placement_area=placement_area, is_active=True)
    filters &= Q(start_date__lte=now) | Q(start_date__isnull=True)
    filters &= Q(end_date__gte=now) | Q(end_date__isnull=True)
    
    if ad_type:
        filters &= Q(ad_type=ad_type)
    
    available_ads = Advertisement.objects.filter(filters).order_by('-priority', '?')
    
    # Filter by category if provided
    if post_category_id and available_ads.exists():
        category_filtered_ads = []
        for ad in available_ads:
            if ad.target_categories.exists():
                if ad.target_categories.filter(id=post_category_id).exists():
                    category_filtered_ads.append(ad)
            else:
                category_filtered_ads.append(ad)
        
        if category_filtered_ads:
            available_ads = category_filtered_ads
    
    # Apply display limits and return requested count
    ads_with_limits = []
    for ad in available_ads:
        if ad.max_display_count == 0 or ad.impressions < ad.max_display_count:
            ads_with_limits.append(ad)
        if len(ads_with_limits) >= count:
            break
    
    # Increment impressions for selected ads
    for ad in ads_with_limits:
        ad.impressions += 1
        ad.save(update_fields=['impressions'])
    
    return ads_with_limits

def select_ad_by_strategy(ads):
    """Select an ad based on display strategy with fallback"""
    if not ads:
        return None
    
    # Group ads by strategy (you'll need to add display_strategy field to your model)
    # For now, we'll use priority-based weighted selection as default
    
    # If we have display_strategy field, uncomment below:
    """
    random_ads = [ad for ad in ads if ad.display_strategy == 'RANDOM']
    weighted_ads = [ad for ad in ads if ad.display_strategy == 'WEIGHTED']
    sequential_ads = [ad for ad in ads if ad.display_strategy == 'SEQUENTIAL']
    
    if weighted_ads:
        return select_weighted_ad(weighted_ads)
    elif sequential_ads:
        return select_sequential_ad(sequential_ads)
    elif random_ads:
        return random.choice(random_ads)
    else:
    """
    # Default: weighted selection by priority
    return select_weighted_ad(ads)

def select_weighted_ad(ads):
    """Select ad based on priority weights"""
    if not ads:
        return None
    
    # Create weights based on priority (ensure positive weights)
    weights = [max(ad.priority, 1) for ad in ads]
    
    # Use weighted random selection
    return random.choices(ads, weights=weights, k=1)[0]

def select_sequential_ad(ads):
    """Select next ad in sequence (round-robin by impressions)"""
    if not ads:
        return None
    
    # Sort by impressions (least shown first)
    return sorted(ads, key=lambda x: x.impressions)[0]

@register.simple_tag
def track_ad_click(ad_id):
    """Template tag to handle ad click tracking"""
    try:
        ad = Advertisement.objects.get(id=ad_id)
        ad.clicks += 1
        ad.save(update_fields=['clicks'])
        return f"Ad click tracked for {ad.name}"
    except Advertisement.DoesNotExist:
        return ""
    
@register.simple_tag
def get_sidebar_ads():
    """Return active sidebar ads (default 3)"""
    return get_multiple_ads('sidebar', count=3)
