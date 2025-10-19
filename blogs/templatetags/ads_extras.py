# blogs/templatetags/ads_extras.py
from django import template
from django.db.models import Q
from blogs.models import Advertisement
from django.utils import timezone
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def get_ad(placement, category_id):
    """
    Fetches and returns ad content for the specified placement and category.
    Returns empty string if no ads found.
    """
    now = timezone.now()
    
    try:
        # Get active ads for this placement
        ads = Advertisement.objects.filter(
            is_active=True,
            placement_area=placement,
            start_date__lte=now,
            end_date__gte=now
        )
        
        # Filter for category targeting
        filtered_ads = ads.filter(
            Q(target_categories__id=category_id) | Q(target_categories__isnull=True)
        ).distinct().order_by('-priority')
        
        if filtered_ads.exists():
            ad = filtered_ads.first()
            
            # Track impression
            ad.impressions += 1
            ad.save()
            
            return mark_safe(ad.ad_code)
        else:
            return ""
                    
    except Exception as e:
        # Log error in production
        return ""