from django.db import models
from django.utils import timezone
from django.conf import settings


# Friends List Model
class FriendsList(models.Model):
    user                    = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user')
    friends                 = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='friends')


    class Meta:
        verbose_name = "FriendsList"
        verbose_name_plural = "FriendsLists"

    def __str__(self):
        return self.user.username

    def add_friend(self, friend):
        # Add a new friend
        if not friend in self.friends.all():
            self.friends.add(friend)

    def remove_friend(self, friend):
        # Remove  a friend
        if friend in self.friends.all():
            self.friends.remove(friend)

    
    def unfriend(self, removee):
        """
        Initiate the action of unfriending someone.
        """
        remover_friends_list = self # person terminating the friendship

        # Remove friend from remover friend list
        remover_friends_list.remove_friend(removee)

        # Remove friend from removee friend list
        friends_list = FriendsList.objects.get(user=removee)
        friends_list.remove_friend(remover_friends_list.user)
        

    def is_matual_friend(self, friend):
        # Are We Friends?
        if friend in self.friends.all():
            return True
        else:
            return False


# Friend Request Model
class FriendRequest(models.Model):
    """
    A friend request consists of two main parts:
        1. SENDER
            - Person sending/initiating the friend request
        2. RECIVER
            - Person receiving the friend friend
    """
    
    sender                     = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sender')
    receiver                   = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='receiver')
    is_active                  = models.BooleanField(default=True, blank=False, null=False)
    timestamp                  = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "FriendRequest"
        verbose_name_plural = "FriendRequests"

    def __str__(self):
        return self.sender.username
        


    def accept(self):
        """
        Accept a friend request.
        Update both SENDER and RECEIVER friend lists.
        """

        receiver_friend_list = FriendsList.objects.get(user=self.receiver)

        if receiver_friend_list:
            receiver_friend_list.add_friend(self.sender)

            sender_friend_list = FriendsList.objects.get(user=self.sender)

            if sender_friend_list:
                sender_friend_list.add_friend(self.receiver)
                self.is_active = False
                self.save()


    def decline(self):
        """
        Decline a friend request.
        Is it "declined" by setting the `is_active` field to False
        """
        self.is_active = False
        self.save()

    def cancel(self):
        """
        Cancel a friend request.
        Is it "cancelled" by setting the `is_active` field to False.
        This is only different with respect to "declining" through the notification that is generated.
        """
        self.is_active = False
        self.save()

        

