from django.db import models


class Group(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    slug = models.SlugField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Message(models.Model):
    from_user = models.ForeignKey('users.User', related_name='messages_from', on_delete=models.CASCADE, db_index=True)
    to_user = models.ForeignKey('users.User', related_name='messages_to', on_delete=models.CASCADE, null=True)
    to_group = models.ForeignKey('Group', related_name='messages', on_delete=models.CASCADE, null=True)
    content = models.TextField(max_length=3000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                name="%(app_label)s_%(class)s_file_parent",
                #  Only one of to_user, to_group should be set else raise error
                check=(
                    models.Q(
                        to_user__isnull=False,
                        to_group__isnull=True,
                    )
                    | models.Q(
                        to_user__isnull=True,
                        to_group__isnull=False,
                    )
                ),
            )
        ]
