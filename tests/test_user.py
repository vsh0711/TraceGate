from agent.user import REMINDER, ScriptedUser

YES, BYE = "Yes, please go ahead.", "No, that is all. Thank you."
ID = "Hi, my email is a@b.com and my zip code is 94107. "


def test_question_gets_next_scripted_reply():
    u = ScriptedUser([ID + "Please cancel order O1002.", YES, BYE])
    assert u.first().endswith("O1002.")
    assert u.reply("Do you confirm that I cancel O1002?") == YES


def test_statement_after_the_action_ends_the_conversation():
    u = ScriptedUser([ID + "Please cancel order O1002.", YES, YES, BYE])
    u.reply("Shall I cancel it?")
    assert u.reply("Order O1002 is cancelled.") is None      # no second "yes" that pushes a repeat


def test_planned_followup_is_sent_after_a_statement():
    u = ScriptedUser([ID + "Refund $300 for order O1028.", "Then refund the maximum.", YES, BYE])
    assert u.reply("I cannot refund more than the order total of $220.") == "Then refund the maximum."


def test_two_requests_get_one_reminder_only():
    u = ScriptedUser([ID + "Cancel O1002, and refund order O1001.", YES, YES, BYE])
    assert u.reply("I cancelled O1002.") == REMINDER
    assert u.reply("Done.") is None


def test_identity_sentence_does_not_count_as_two_requests():
    u = ScriptedUser([ID + "Please cancel order O1002.", YES, BYE])
    assert u.reply("Done.") is None


def test_no_reply_when_the_script_is_empty():
    assert ScriptedUser([ID + "Hello."]).reply("Anything else?") is None
