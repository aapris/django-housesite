from __future__ import unicode_literals

from django.db import models
from django.db.models import Count
from django.shortcuts import render

from modelcluster.fields import ParentalKey

from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.fields import RichTextField

from wagtail.wagtailcore.models import Page, Orderable
from wagtail.wagtailadmin.edit_handlers import (FieldPanel,
                                                InlinePanel,
                                                MultiFieldPanel,
                                                PageChooserPanel)
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailsearch import index

from wagtail.wagtaildocs.models import Document
from wagtail.wagtaildocs.edit_handlers import DocumentChooserPanel
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from modelcluster.tags import ClusterTaggableManager
from taggit.models import TaggedItemBase


# This is the root home page
class HomePage(Page):
    body = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('body', classname="full")
    ]


class NewssheetPageTag(TaggedItemBase):
    content_object = ParentalKey('home.NewssheetPage', related_name='tagged_items')


class NewssheetPage(Page):
    body = RichTextField(blank=True)
    date = models.DateField("News sheet date")
    public = models.BooleanField(default=False)
    tags = ClusterTaggableManager(through=NewssheetPageTag, blank=True)


# TODO: This could be in NewssheetPage class?
NewssheetPage.content_panels = Page.content_panels + [
    # DocumentChooserPanel('attachments'),
    FieldPanel('body', classname="full"),
    FieldPanel('date'),
    FieldPanel('public'),
    FieldPanel('tags', classname="Tagit"),
    InlinePanel('attachments', label="Attachments"),
    # DocumentChooserPanel('advert_placements'),
]


class NewssheetPageAttachments(models.Model):
    attachment = models.ForeignKey(
        'wagtaildocs.Document',
        null=True,
        blank=True,
        related_name='+'
    )
    text = models.CharField(max_length=255)
    page = ParentalKey('NewssheetPage', related_name='attachments')

    panels = [
        DocumentChooserPanel('attachment'),
        FieldPanel('text'),
    ]

    def __str__(self):
        return self.text


class NewssheetIndexPage(Page):
    intro = RichTextField(blank=True)
    subpage_types = ['home.NewssheetPage', ]

    content_panels = Page.content_panels + [
        FieldPanel('intro', classname="full"),
        # InlinePanel('related_links', label="Related links"),
    ]

    def serve(self, request):
        # Get blogs
        newssheets = self.newssheets

        # Filter by tag
        tag = request.GET.get('tag')
        if tag:
            newssheets = newssheets.filter(tags__name=tag)

        # all_tags = NewssheetPageTag.objects.all()
        # print(dir(all_tags[0]))
        all_tags = NewssheetPageTag.objects.values('tag__name').annotate(occurrences=Count('tag'))
        print(all_tags)
        # for t in all_tags:
        #     print(t)
        return render(request, self.template, {
            'self': self,
            'page': self,
            'newssheets': newssheets,
            'all_tags': all_tags,
        })

    @property
    def newssheets(self):
        # Get list of live blog pages that are descendants of this page
        newssheets = NewssheetPage.objects.live().descendant_of(self)

        # Order by most recent date first
        newssheets = newssheets.order_by('-date')

        return newssheets


    def get_context(self, request):
        # Get newssheets
        newssheets = self.newssheets

        # Filter by tag
        tag = request.GET.get('tag')
        if tag:
            newssheets = newssheets.filter(tags__name=tag)

        # Pagination
        page = request.GET.get('page')
        paginator = Paginator(newssheets, 10)  # Show 10 newssheets per page
        try:
            newssheets = paginator.page(page)
        except PageNotAnInteger:
            newssheets = paginator.page(1)
        except EmptyPage:
            newssheets = paginator.page(paginator.num_pages)

        # Update template context
        context = super(NewssheetIndexPage, self).get_context(request)
        context['newssheets'] = newssheets
        return context


class BlogPage(Page):
    main_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    date = models.DateField("Post date")
    intro = models.CharField(max_length=250)
    body = RichTextField(blank=True)

    search_fields = Page.search_fields + (
        index.SearchField('intro'),
        index.SearchField('body'),
    )

    content_panels = Page.content_panels + [
        FieldPanel('date'),
        ImageChooserPanel('main_image'),
        FieldPanel('intro'),
        FieldPanel('body'),
    ]


class LinkFields(models.Model):
    link_external = models.URLField("External link", blank=True)
    link_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        related_name='+'
    )

    @property
    def link(self):
        if self.link_page:
            return self.link_page.url
        else:
            return self.link_external

    panels = [
        FieldPanel('link_external'),
        PageChooserPanel('link_page'),
    ]

    class Meta:
        abstract = True


# Related links
class RelatedLink(LinkFields):
    title = models.CharField(max_length=255, help_text="Link title")

    panels = [
        FieldPanel('title'),
        MultiFieldPanel(LinkFields.panels, "Link"),
    ]

    class Meta:
        abstract = True


class BlogIndexPage(Page):
    intro = RichTextField(blank=True)
    subpage_types = ['home.BlogPage', ]

    content_panels = Page.content_panels + [
        FieldPanel('intro', classname="full"),
        InlinePanel('related_links', label="Related links"),
    ]


class BlogIndexRelatedLink(Orderable, RelatedLink):
    page = ParentalKey('BlogIndexPage', related_name='related_links')
